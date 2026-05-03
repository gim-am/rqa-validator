from typing import List
import polars as pl

from ...common.list_matching import match_list

from ...validators.helpers import get_data_loaded_columns, get_data_loaded_sheets, get_data_sheet_ids

from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, ValidationResult, SeverityLevel




class SurveyChoicesCheck(BaseValidator):
    """Checks that clean_data values are valid when they come from
    kobo select_one or select_multiple quesitons.
    """
    def __init__(self,
                 schema: BaseDatasetSchema,
                 survey_sheet: str = 'kobo_survey',
                 survey_type_column: str = 'type',
                 survey_name_column: str = 'name',
                 choices_sheet: str = 'kobo_choices',
                 choices_name_column: str = 'name',
                 choices_list_name_column: str = 'list_name',
                 check_sheets: List = ['clean_data']) -> None:
        """

        Args:
            schema (BaseDatasetSchema): dataset schema
            survey_sheet (str, optional): name of the kobo survey sheet in excel. Defaults to 'kobo_survey'.
            survey_type_column (str, optional): name of the type column in the kobo survey sheet. Defaults to 'type'.
            survey_name_column (str, optional): name of the name column in the kobo survey sheet. Defaults to 'name'.
            choices_sheet (str, optional): name of the kobo choices sheet in excel. Defaults to 'kobo_choices'.
            choices_name_column (str, optional): name of the name column in the kobo choices sheet. Defaults to 'name'.
            choices_list_name_column (str, optional): name of the list_name column in the kobo choices sheet. Defaults to 'list_name'.
            check_sheets (List, optional): schema sheet names to check. Defaults to ['clean_data'].
        """
        self.survey_sheet = survey_sheet
        self.check_sheets = check_sheets
        self.survey_type_column = survey_type_column
        self.survey_name_column = survey_name_column
        self.choices_sheet = choices_sheet
        self.choices_name_column = choices_name_column
        self.choices_list_name_column = choices_list_name_column
        self.schema = schema

    @property
    def name(self) -> str:
        return 'SurveyChoicesCheck'
    
    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks that clean_data values are valid when they come from
    kobo select_one or select_multiple quesitons.

        This process: 
            -performs prevalidation to make sure expected sheets, columns etc
                are present
            - performs some transformations on the kobo questions and choices
            - for each check_sheet, gets the relevant questions, builds an expression
                to check for valid values and records invalid values.
            - the process to build an expression is slightly different for
                select_one and select_multiple as they have to handle
                spaces in values differntly. see comments in the code for details.     
    
        Args:
            data (ExcelLoaderData): excel data to validate

        Returns:
            List[ValidationResult]: list of validation errors
        """
        results: List[ValidationResult] = []
        # kobo quesiton types to find
        column_selector = r"select_one|select_multiple"
        # pre-validation

        result, data_loaded_sheets = get_data_loaded_sheets(data=data, 
                                                       sheet_names=[self.survey_sheet,
                                                                    self.choices_sheet, 
                                                                    *self.check_sheets],
                                                        rule=self.name)

        if result:
            results.extend(result)
            return results
        
        result, data_loaded_columns = get_data_loaded_columns(data = {self.survey_type_column: data_loaded_sheets[self.survey_sheet],
                                                                      self.survey_name_column: data_loaded_sheets[self.survey_sheet],
                                                                      self.choices_name_column: data_loaded_sheets[self.choices_sheet],
                                                                      self.choices_list_name_column: data_loaded_sheets[self.choices_sheet]},
                                                        rule=self.name)

        if result:
            results.extend(result)
            return results       
        
        
        search_items = {key: data_loaded_sheets[key] for key in self.check_sheets}
        result, data_id_columns = get_data_sheet_ids(schema=self.schema, data=search_items, rule=self.name)

        if result:
            results.extend(result)
            return results
        
        # get the choices and turn it into a dict
        choices_dict = (
                data_loaded_sheets[self.choices_sheet].data
                                                    .select([ data_loaded_columns[self.choices_list_name_column].data_column_name, 
                                                             pl.col(data_loaded_columns[self.choices_name_column].data_column_name)
                                                             .str.to_lowercase()
                                                             .str.replace(r'_', '', n=-1)
                                                             .str.strip_chars(' ')])
                                                             .group_by(data_loaded_columns[self.choices_list_name_column].data_column_name)
                                                             .agg(v_list=pl.col(data_loaded_columns[self.choices_name_column].data_column_name).implode())
                                                             .with_columns(pl.col("v_list").alias("values"))
                                                             .select([data_loaded_columns[self.choices_list_name_column].data_column_name, 
                                                                      "values"])
                                                                      .to_dicts()
                                                                      )

        choices_dict = {row[data_loaded_columns[self.choices_list_name_column].data_column_name]: row["values"] for row in choices_dict}

        # get the survey questions that are selected from a list
        # and transform the data
        survey_category_questions_df = data_loaded_sheets[self.survey_sheet].data \
                                        .select([data_loaded_columns[self.survey_type_column].data_column_name, 
                                                 data_loaded_columns[self.survey_name_column].data_column_name]) \
                                            .filter(pl.col(data_loaded_columns[self.survey_type_column].data_column_name)
                                                    .str
                                                    .contains(column_selector)) \
                                            .with_columns(pl.col(data_loaded_columns[self.survey_type_column].data_column_name)
                                                        .str.split(" ")
                                                        .list.to_struct(fields=['type_only', 'choice_list_name'])
                                                        .alias("choice_list_name")
                                                        ).unnest('choice_list_name')
        # split out the question types
        survey_category_questions_select_one = survey_category_questions_df.filter(pl.col('type_only') == "select_one")\
                                                        .select([data_loaded_columns[self.survey_name_column].data_column_name])\
                                                        .unique().to_series().str.to_lowercase().to_list()

        survey_category_questions_select_multiple = survey_category_questions_df.filter(pl.col('type_only') == "select_multiple")\
                                                        .select([data_loaded_columns[self.survey_name_column].data_column_name])\
                                                        .unique().to_series().str.to_lowercase().to_list()
        survey_question_choices_dict = (survey_category_questions_df.select([pl.col(data_loaded_columns[self.survey_name_column].data_column_name)
                                                                             .str.to_lowercase(), 
                                                                             'choice_list_name'])
                                                                             .to_dicts())

        survey_question_choices_dict =  {row[data_loaded_columns[self.survey_name_column].data_column_name]: row["choice_list_name"] for row in survey_question_choices_dict}



        for sheet in self.check_sheets:
            # only check the questions that are present on the sheet
            filtered_questions_select_one = match_list(survey_category_questions_select_one, 
                                                       data_loaded_sheets[sheet].data.columns)
            filtered_questions_select_multiple = match_list(survey_category_questions_select_multiple, 
                                                            data_loaded_sheets[sheet].data.columns)
            filtered_questions = filtered_questions_select_one + filtered_questions_select_multiple

            difference_expressions = []

            # build an expression to find values that dont match
            # for each question, compare the values in the survey choices
            # to the values in the data sheet. 
            # currently leading/trailing spaces, _ characters are replaced and the 
            # values are made lowercase.
            
            # because multiple_select questions store data as a space delimited values, 
            # these values need to be split and compared individually
            # in the event that a survey choice option has a space in it this process
            # will throw an error for the value being checked

            for question in filtered_questions_select_multiple:
                col_has_difference = f"{question}_has_difference"
                valid_choices: List[str] = choices_dict[survey_question_choices_dict[question]]
                
                difference_expression =( pl.when(pl.col(question).is_not_null() )
                                                .then(pl.col(question)
                                                      .str.split(" ")
                                                      .list.eval(pl.element()
                                                                 .str.to_lowercase()
                                                                 .str.replace(r'_', '', n=-1)
                                                                 .str.strip_chars(' ')
                                                                .is_in(valid_choices)
                                                                .not_()
                                                                )
                                                                .list.any() )\
                                            .otherwise(False)
                                            .alias(col_has_difference))
                
                difference_expressions.append(difference_expression)
            # build an expression to find values that dont match
            # for each question, compare the values in the survey choices
            # to the values in the data sheet. 
            # currently leading/trailing spaces, _ characters are replaced and the 
            # values are made lowercase.

            # choice values with spaces should not cause errors in this check 

            for question in filtered_questions_select_one:
                col_has_difference = f"{question}_has_difference"
                valid_choices: List[str] = choices_dict[survey_question_choices_dict[question]]
                
                difference_expression =( pl.when(pl.col(question).is_not_null() )
                                                .then(pl.col(question)
                                                      .str.to_lowercase()
                                                      .str.replace(r'_', '', n=-1)
                                                      .str.strip_chars(' ')
                                                      .is_in(valid_choices)
                                                      .not_())\
                                            .otherwise(False)
                                            .alias(col_has_difference))
                
                difference_expressions.append(difference_expression)

            # Get the invalid values
            comparison_df = data_loaded_sheets[sheet].data.with_columns(difference_expressions)
            has_any_change = pl.any_horizontal([pl.col(f"{question}_has_difference") for question in filtered_questions])
            changes_only = comparison_df.filter(has_any_change)

            output_rows = []

            check_sheet_id_column = data_id_columns[sheet][0]  
            # report the invalid values if any
            if not changes_only.is_empty():
                for row in changes_only.iter_rows(named=True):
                    uuid = row[check_sheet_id_column.data_column_name]
                    for question in filtered_questions:
                        is_changed = row[f"{question}_has_difference"]

                        if is_changed:
                            old_val = row[question]
                            output_rows.append({
                                'uuid': uuid,
                                "question": question,
                                "invalid_value": old_val
                            })

                difference_df = pl.DataFrame(output_rows, infer_schema_length=None)
                if difference_df.height > 0:
                    # df_to_csv(data=difference_df, filename=validation_results_filename)
                    results.append(ValidationResult(
                        rule = self.name,
                        message = f'There were {difference_df.height} values found in the {sheet} sheet that were not reflected in the {self.survey_sheet} sheet. Check the output for details.'
                        ,severity = SeverityLevel.ERROR
                        ,sheet_name=sheet
                        , details=difference_df.to_dict()
                    ))
           

        return results