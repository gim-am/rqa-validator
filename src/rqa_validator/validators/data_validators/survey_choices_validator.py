from typing import List
import polars as pl

from ...common.list_matching import match_list, filter_loaded_sheets

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
                 check_sheets: List = ['clean_data'],
                 select_multiple_value_separator: str = ' ') -> None:
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
            select_multiple_value_separator (str, optional): select_multiple value separator. Defaults to ' '.
        """
        self.schema = schema
        self.survey_sheet = survey_sheet
        self.check_sheets = check_sheets
        self.survey_type_column = survey_type_column
        self.survey_name_column = survey_name_column
        self.choices_sheet = choices_sheet
        self.choices_name_column = choices_name_column
        self.choices_list_name_column = choices_list_name_column
        # select_multiple values are stored as one value separated by delimiter
        self.select_multiple_value_separator = select_multiple_value_separator


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
        
        
        filtered_loaded_sheets = filter_loaded_sheets(self.check_sheets, data_loaded_sheets)
        result, data_id_columns = get_data_sheet_ids(schema=self.schema, data=filtered_loaded_sheets, rule=self.name)

        if result:
            results.extend(result)
            return results
        
        # get the choices and turn it into a dict
        choices_dict = (
                data_loaded_sheets[self.choices_sheet].data
                                                    .select([ pl.col(data_loaded_columns[self.choices_list_name_column].data_column_name)
                                                                .str.strip_chars(' '), 
                                                             pl.col(data_loaded_columns[self.choices_name_column].data_column_name)
                                                             .str.to_lowercase()
                                                             .str.replace(r'_', '', n=-1)
                                                             .str.strip_chars(' ')])
                                                            .filter(pl.col(data_loaded_columns[self.choices_list_name_column].data_column_name).is_not_null() &
                                                                    (pl.col(data_loaded_columns[self.choices_list_name_column].data_column_name) != ''))
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
                                                        .str.replace(r"[\"']", '')
                                                        .str.strip_chars(' ')
                                                        .str.split(" ")
                                                        .list.to_struct(fields=['type_only', 'choice_list_name'])
                                                        .alias("choice_list_name")
                                                        ).unnest('choice_list_name') \
                                            .filter(pl.col('choice_list_name').is_not_null() &
                                                    (pl.col('choice_list_name') != '')) \
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
            filtered_questions_select_one: List[str] = match_list(survey_category_questions_select_one, 
                                                       data_loaded_sheets[sheet].data.columns)
            filtered_questions_select_multiple:List[str]  = match_list(survey_category_questions_select_multiple, 
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
                                                      .str.split(self.select_multiple_value_separator)
                                                      .list.eval(pl.element()
                                                                 .cast(pl.Utf8)
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
                                                      .cast(pl.Utf8)
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

            check_sheet_id_column = data_id_columns[sheet][0]  
            # report the invalid values if any
            # transform data from a wide format to a long format and join to flags. this allows for
            # filtering invalid values in a single operation
            if not changes_only.is_empty():
                values_df = changes_only.unpivot(
                index=[check_sheet_id_column.data_column_name],
                on=filtered_questions,
                variable_name="question",
                value_name="invalid_value"
                )

                # unpivot flags. Extract question name from flag column name
                flags_df = changes_only.unpivot(
                    index=[check_sheet_id_column.data_column_name],
                    on=[f"{c}_has_difference" for c in filtered_questions],
                    variable_name="flag_col_name", 
                    value_name="is_changed"
                    ).with_columns(
                        pl.col("flag_col_name")
                        .str.replace("^is_", "", literal=False)
                        .str.replace("_has_difference$", "", literal=False)
                        .alias("question")
                        )
                
                merged_df = values_df.join(
                    flags_df,
                    on=[check_sheet_id_column.data_column_name, "question"],
                    how="inner"
                ).filter(pl.col("is_changed") )

                difference_df = merged_df.select([
                    pl.col(check_sheet_id_column.data_column_name).alias('uuid'),
                    pl.lit(sheet).alias("sheet"),
                    pl.col("question"),
                    pl.col("invalid_value").cast(pl.Utf8)
                ])

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