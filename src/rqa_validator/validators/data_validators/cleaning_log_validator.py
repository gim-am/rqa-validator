from ...common.file_export import df_to_csv
from ...common.list_matching import filter_list, match_list, match_sheet_columns
from ...common.schema_matching import get_matching_unique_columns
from ...common.expression_builder import create_column_difference_expression
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ..base import BaseValidator, ValidationResult


import polars as pl


from typing import List


class CleaningLog(BaseValidator):
    """This process performs two steps to validate the data in the cleaning log
    
    After making sure that the required sheets and columns have been loaded and matched:

    - The first step validates that all the items in a cleaning log are reflected in the clean data.

    - The second step compares the differences between the clean and raw data sheets 
    and then checks that all these differences are reflected in the cleaning log

    The output includes:
    - items in cleaning log that have multiple updates for the same question
    - questions in cleaning log that are not present in clean_data
    - items where there is a difference between cleaning_log and clean_data values
    - items where there is a difference between raw_data/clean_data and the cleaning log

    """
    def __init__(self, schema: BaseDatasetSchema,
                 clean_data_sheet:str = 'clean_data',
                 raw_data_sheet: str = 'raw_data',
                 cleaning_log_sheet: str = 'cleaning_log',
                 cleaning_log_new_value_column:str = 'new_value',
                 cleaning_log_old_value_column:str = 'old_value',
                 cleaning_log_question_column:str = 'question',
                 cleaning_log_change_type_column:str = 'change_type') -> None:
        """Validates that the items in a cleaning log are reflected in the clean data

        Args:
            schema (BaseDatasetSchema): dataset schema for the dataset
            clean_data_sheet (str, optional): name of the clean data sheet. Defaults to 'clean_data'.
            raw_data_sheet (str, optional): name of the raw data sheet. Defaults to 'raw_data'.
            cleaning_log_sheet (str, optional): name of the cleaning log sheet. Defaults to 'cleaning_log'.
            cleaning_log_new_value_column (str, optional): name of the cleaning log new value column. Defaults to 'new_value'.
            cleaning_log_old_value_column (str, optional): name of the cleaning log old value column. Defaults to 'old_value'.
            cleaning_log_question_column (str, optional): name of the cleaning log quesitons column. Defaults to 'question'.
            cleaning_log_change_type_column (str, optional): name of the cleaning log change_type column. Defaults to 'change_type'
        """
        self.schema = schema
        self.clean_data_sheet = clean_data_sheet
        self.raw_data_sheet = raw_data_sheet
        self.cleaning_log_sheet = cleaning_log_sheet
        self.cleaning_log_new_value_column = cleaning_log_new_value_column
        self.cleaning_log_old_value_column = cleaning_log_old_value_column
        self.cleaning_log_question_column = cleaning_log_question_column
        self.cleaning_log_change_type_column = cleaning_log_change_type_column
        # the ProcessValueMap that contains the list of possible values needed in cleaning_log_change_type_column
        self.process_value_map_name = 'cleaning_log_validation'


    @property
    def name(self) -> str:
        return 'CleaningLog'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """This process performs two steps to validate the data in the cleaning log
    
        After making sure that the required sheets and columns have been loaded and matched:

        - The first step validates that all the items in a cleaning log are reflected in the clean data.

        - The second step compares the differences between the clean and raw data sheets 
        and then checks that all these differences are reflected in the cleaning log

        The output includes:
        - items in cleaning log that have multiple updates for the same question
        - questions in cleaning log that are not present in clean_data
        - items where there is a difference between cleaning_log and clean_data values
        - items where there is a difference between raw_data/clean_data and the cleaning log

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        multiple_changes_filename = 'cleaning_log_validation_multiple_changes'
        validation_results_filename = 'cleaning_log_validation_results'

        # PRE-VALIDATION - check sheets, columns etc all exist

        clean_data_loaded_sheet = data.get_loaded_sheet(self.clean_data_sheet)

        if not clean_data_loaded_sheet:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {self.clean_data_sheet} is expected.'
                ,severity = 'error'
            ))
            return results
        
        raw_data_loaded_sheet = data.get_loaded_sheet(self.raw_data_sheet)

        if not raw_data_loaded_sheet:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {self.raw_data_sheet} is expected.'
                ,severity = 'error'
            ))
            return results

        cleaning_log_schema_sheet = self.schema.get_schema_loaded_sheet(self.cleaning_log_sheet)
        if not cleaning_log_schema_sheet:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A schema sheet for {self.cleaning_log_sheet} is expected.'
                ,severity = 'error'
            ))
            return results

        # get id column
        clean_data_sheet_ids = get_matching_unique_columns(self.schema, clean_data_loaded_sheet, self.clean_data_sheet)

        if not clean_data_sheet_ids:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A unique id column for {clean_data_loaded_sheet.data_sheet_name} is expected but none were found.'
                ,severity = 'error'
                , sheet_name =  clean_data_loaded_sheet.data_sheet_name
                # , column_name = ', '.join(master_matching_columns)
            ))
            return results
        
        raw_data_sheet_ids = get_matching_unique_columns(self.schema, raw_data_loaded_sheet, self.raw_data_sheet)

        if not raw_data_sheet_ids:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A unique id column for {raw_data_loaded_sheet.data_sheet_name} is expected but none were found.'
                ,severity = 'error'
                , sheet_name =  raw_data_loaded_sheet.data_sheet_name
                # , column_name = ', '.join(master_matching_columns)
            ))
            return results

        cleaning_log_loaded_sheet = data.get_loaded_sheet(self.cleaning_log_sheet)
        # wont have a unique column as ids can have multiple updates in the log
        if not cleaning_log_loaded_sheet:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {self.cleaning_log_sheet} is expected.'
                ,severity = 'error'
            ))
            return results

        # make sure that the cleaning log has the columns needed
        cleaning_log_new_value_column = cleaning_log_loaded_sheet.get_column_map(self.cleaning_log_new_value_column)
        if cleaning_log_new_value_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.cleaning_log_new_value_column} is expected.'
                ,severity = 'error'
                , sheet_name= self.cleaning_log_sheet
            ))
            return results

        cleaning_log_old_value_column = cleaning_log_loaded_sheet.get_column_map(self.cleaning_log_old_value_column)
        if cleaning_log_old_value_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.cleaning_log_old_value_column} is expected.'
                ,severity = 'error'
                , sheet_name= self.cleaning_log_sheet
            ))
            return results

        cleaning_log_question_column = cleaning_log_loaded_sheet.get_column_map(self.cleaning_log_question_column)
        if cleaning_log_question_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.cleaning_log_question_column} is expected.'
                ,severity = 'error'
                , sheet_name= self.cleaning_log_sheet
            ))
            return results

        cleaning_log_change_type_column = cleaning_log_loaded_sheet.get_column_map(self.cleaning_log_change_type_column)
        if cleaning_log_change_type_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.cleaning_log_change_type_column} is expected.'
                ,severity = 'error'
                , sheet_name= self.cleaning_log_sheet
            ))
            return results


        schema_change_type_column = cleaning_log_schema_sheet.get_column(self.cleaning_log_change_type_column)
        if schema_change_type_column is None:
            # this should already have been validated when checking mandatory columns
            return results

        schema_change_type_values = schema_change_type_column.get_process_values(self.process_value_map_name)

        if schema_change_type_values is None or len(schema_change_type_values.values) == 0:
            results.append(ValidationResult(
                rule = self.name,
                message = f'process_values were expected for column {self.cleaning_log_change_type_column} for process {self.process_value_map_name}.'
                ,severity = 'error'
                , sheet_name= self.cleaning_log_sheet
                , column_name=self.cleaning_log_change_type_column
            ))
            return results

        clean_to_log_matching_id_columns = match_sheet_columns(clean_data_sheet_ids, cleaning_log_loaded_sheet.column_map)
        # should only be one matching id column between the sheets.
        if len(clean_to_log_matching_id_columns) != 1:
            results.append(ValidationResult(
                rule = self.name,
                message = f'Expected 1 linkable ID column for sheets {self.clean_data_sheet} and {self.cleaning_log_sheet} but {len(clean_to_log_matching_id_columns)} were found.'
                ,severity = 'error'
            ))
            return results

        clean_data_id_columns = clean_to_log_matching_id_columns[0]
        
        cleaning_log_id_column = cleaning_log_loaded_sheet.get_column_map(clean_data_id_columns.schema_column_name)

        if cleaning_log_id_column is None:
            # should not happen as it was just matched/checked
            results.append(ValidationResult(
                rule = self.name,
                message = f'Expected to find a column for {clean_data_id_columns.schema_column_name} in sheet {self.cleaning_log_sheet} but none was found.'
                ,severity = 'error'
            ))
            return results
        
        raw_to_clean_matching_id_columns = match_sheet_columns(raw_data_sheet_ids, clean_data_loaded_sheet.column_map)
        # should only be one matching id column between the sheets.
        if len(raw_to_clean_matching_id_columns) != 1:
            results.append(ValidationResult(
                rule = self.name,
                message = f'Expected 1 linkable ID column for sheets {self.clean_data_sheet} and {self.raw_data_sheet} but {len(raw_to_clean_matching_id_columns)} were found.'
                ,severity = 'error'
            ))
            return results

        raw_data_id_columns = raw_to_clean_matching_id_columns[0]

        # TRANSFORMATION: transforms data in preparation for comparison   
            # the two processes are stored in seperate functions just to
            # make distinguishing the logic between them easier
         # dataframe of actual changes made
        modified_rows_df = cleaning_log_loaded_sheet.data.filter(pl.col(cleaning_log_change_type_column.data_column_name) \
                                                                    .str.to_lowercase().is_in(schema_change_type_values.values) ) \
                                                        .select([cleaning_log_id_column.data_column_name,
                                                                    cleaning_log_new_value_column.data_column_name,
                                                                    cleaning_log_old_value_column.data_column_name,
                                                                    cleaning_log_change_type_column.data_column_name,
                                                                    cleaning_log_question_column.data_column_name])
        
        def _compare_raw_to_clean_to_log(self):
            """Gets the difference between raw and clean sheets and compares 
            this to the cleaning log"""
            # get columns that are in both clean and raw sheets
            # then filter the sheets
            clean_data_columns = filter_list(match_list(clean_data_loaded_sheet.data.columns, 
                                                                raw_data_loaded_sheet.data.columns), 
                                            [clean_data_id_columns.data_column_name])
                                            
            clean_data_filtered_df = clean_data_loaded_sheet.data.select([clean_data_id_columns.data_column_name] + clean_data_columns)
            raw_data_filtered_df = raw_data_loaded_sheet.data.select([raw_data_id_columns.data_column_name] + clean_data_columns) \
                                                            .rename({f"{q}": f"{q}_original_value"
                                                                            for q in clean_data_columns
                                                                    })
            
            # join the dataframes so that only ids in both are compared
            joined_df = raw_data_filtered_df.join(other=clean_data_filtered_df,
                                      left_on=raw_data_id_columns.data_column_name,
                                      right_on= clean_data_id_columns.data_column_name,
                                      how='inner')
            
            difference_expressions = []

            # build expressions to compare the columns of both dataframes
            for question in clean_data_columns:
                difference_expression = create_column_difference_expression(
                            question, 
                            f"{question}_original_value",
                            joined_df.schema[question], 
                            joined_df.schema[f"{question}_original_value"]) \
                    .alias(f"is_{question}_changed")
                
                difference_expressions.append(difference_expression)
            
            # add the difference flags to the dataframe and checl for changes
            comparison_df = joined_df.with_columns(difference_expressions)
            has_any_change = pl.any_horizontal([pl.col(f"is_{question}_changed") for question in clean_data_columns])
            changes_only = comparison_df.filter(has_any_change)
            output_rows = []

            # record the changes
            if not changes_only.is_empty():
                for row in changes_only.iter_rows(named=True):
                    uuid = row[clean_data_id_columns.data_column_name]
                    for question in clean_data_columns:
                        is_changed = row[f"is_{question}_changed"]
                        if is_changed:
                            old_val = row[f"{question}_original_value"]
                            new_val = row[question]
                            output_rows.append({
                                'uuid': uuid,
                                f"{cleaning_log_question_column.data_column_name}": question,
                                f"{cleaning_log_old_value_column.data_column_name}": str(old_val),
                                F"{cleaning_log_new_value_column.data_column_name}": str(new_val)
                            })
                # difference between raw and clean
                difference_raw_to_clean_df = pl.DataFrame(output_rows, infer_schema_length=None)

                # difference between above and cleaning log
                difference_df = difference_raw_to_clean_df.join(other=modified_rows_df,
                                                                how='anti',
                                                                left_on='uuid',
                                                                right_on=cleaning_log_id_column.data_column_name)
                
                if difference_df.height > 0:
                    # df_to_csv(data=difference_df, filename=validation_results_filename)
                    results.append(ValidationResult(
                        rule = self.name,
                        message = f'There were {difference_df.height} differences found in the {self.clean_data_sheet} sheet that were not reflected in the {self.cleaning_log_sheet} sheet. Check the output for details.'
                        ,severity = 'error'
                        ,sheet_name=self.cleaning_log_sheet
                        , details=difference_df.to_dict()
                    ))


        def _compare_log_to_clean(self):           
            """Compares the cleaning log to clean_data
            """
            # racods where the same question was updated more than once for the same id
            multiple_change_mask = modified_rows_df.select(cleaning_log_id_column.data_column_name,
                                                            cleaning_log_question_column.data_column_name,
                                                            ).is_duplicated()

            multiple_change_df = modified_rows_df.filter(multiple_change_mask).sort(cleaning_log_id_column.data_column_name)

            if multiple_change_df.height > 0:
                df_to_csv(data=multiple_change_df, filename = multiple_changes_filename)
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'{multiple_change_df.select(cleaning_log_id_column.data_column_name) \
                                    .n_unique()} Ids had multiple changes for the same question. \
                                These were not validated. Check the output file {multiple_changes_filename} for details.'
                    ,severity = 'warning'
                    ,details = multiple_change_df.to_dict()
                ))

            # scan cleaning log for old value = new value
            same_value_df = modified_rows_df.filter(pl.col(cleaning_log_new_value_column.data_column_name).cast(pl.Utf8) == pl.col(cleaning_log_old_value_column.data_column_name).cast(pl.Utf8)) \
                                                            .select(cleaning_log_id_column.data_column_name,
                                                                    cleaning_log_new_value_column.data_column_name,
                                                                    cleaning_log_old_value_column.data_column_name,
                                                                    cleaning_log_change_type_column.data_column_name)
            if same_value_df.height > 0:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'{same_value_df.height} row/s had {cleaning_log_old_value_column.data_column_name} equal {cleaning_log_new_value_column.data_column_name}. Check the output file {multiple_changes_filename} for details.'
                    ,severity = 'warning'
                    ,details = same_value_df.to_dict()
                ))

            # remove records with multiple chages as there is no way to determine which should
            # be the most recent
            # also remove other columns as they are no longer necessary
            unique_modified_rows_df = modified_rows_df.filter(~multiple_change_mask)\
                                                        .sort(cleaning_log_id_column.data_column_name)\
                                                        .select([cleaning_log_id_column.data_column_name, 
                                                                 cleaning_log_new_value_column.data_column_name,
                                                                 cleaning_log_question_column.data_column_name])

            if unique_modified_rows_df.height < 1:
                return results
            # get a list of questions that had values changed
            questions = unique_modified_rows_df.select(cleaning_log_question_column.data_column_name).unique().to_series().str.to_lowercase().to_list()

            missing_quesitons = filter_list(questions, clean_data_loaded_sheet.data.columns)
            if missing_quesitons:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'The following questions are listed in {cleaning_log_loaded_sheet.data_sheet_name} but were not found in {clean_data_loaded_sheet.data_sheet_name}: {missing_quesitons}.'
                    ,severity = 'Warning'
                ))
                questions = filter_list(questions, missing_quesitons)
                if len(questions) < 1:
                    # if no valid questions left to check
                    return results
                
                # return results

            # add column to specifiy an update. this helps to specify which
            # questions were updated later after the pivot as the pivot will
            # add a column for each question even if that question was not updated
            # for a particular uuid. 
            # The result of this will be that question columns
            # that actually had an update in cleaning log will have 'true' for that question
            # while all other other questions will be null
            # fill null with '' to make comparison easier later
            unique_modified_rows_df = unique_modified_rows_df.with_columns(pl.lit(True).alias('is_update')) \
                                                            .with_columns(pl.col(cleaning_log_new_value_column.data_column_name))#.fill_null(''))

            # pivot the table for use later. lower the questions/column names.
            unique_modified_rows_df = unique_modified_rows_df.pivot(on=cleaning_log_question_column.data_column_name,
                                                            index=cleaning_log_id_column.data_column_name,
                                                            values=[cleaning_log_new_value_column.data_column_name, 'is_update']) \
                                                            .rename(str.lower)
            # rename for later
            unique_modified_rows_df = unique_modified_rows_df.rename({f"new_value_{q}": f"{q}_val"
                                                                                    for q in questions
                                                                            }).rename({
                                                                                f"is_update_{q}": f"{q}_has_update"
                                                                                for q in questions
                                                                            })

            # filter the clean_data sheet to only have records that are in the cleaning log
            # and only select the questions that were present in the cleaning log
            # fill empty values to '' to make comparison easier later
            clean_data_filtered_df = clean_data_loaded_sheet.data.select([clean_data_id_columns.data_column_name] + questions) \
                                                                    .filter(pl.col(clean_data_id_columns.data_column_name).is_in(unique_modified_rows_df[cleaning_log_id_column.data_column_name].implode())) \
                                                                    # .fill_null('')
            # join dataframes so columns can be matched below
            joined_df = unique_modified_rows_df.join(other=clean_data_filtered_df,
                                                        left_on=cleaning_log_id_column.data_column_name,
                                                        right_on=clean_data_id_columns.data_column_name,
                                                        how='left')

            # build expressions to check for differences in the two dataframes
            difference_expressions = []
            for question in questions:
                col_has_update = f"{question}_has_update"
                # Check if the new value exists AND is different from the old value               

                difference_expression = ( 
                            create_column_difference_expression(
                            question, 
                            f"{question}_val",
                            joined_df.schema[question], 
                            joined_df.schema[f"{question}_val"])) \
                    .alias(f"is_{question}_changed")
                
                difference_expression = pl.when(pl.col(col_has_update).is_not_null()) \
                                            .then(difference_expression) \
                                            .otherwise(pl.col(col_has_update).is_not_null())
                

                difference_expressions.append(difference_expression)

            # Add the difference flags to the dataframe
            comparison_df = joined_df.with_columns(difference_expressions)
            # check for changes
            has_any_change = pl.any_horizontal([pl.col(f"is_{question}_changed") for question in questions])
            changes_only = comparison_df.filter(has_any_change)

            output_rows = []

            # record the changes
            if not changes_only.is_empty():
                for row in changes_only.iter_rows(named=True):
                    uuid = row[cleaning_log_id_column.data_column_name]
                    for question in questions:
                        new_col = f"{question}_val"
                        is_changed = row[f"is_{question}_changed"]

                        if is_changed:
                            old_val = row[question]
                            new_val = row[new_col]
                            output_rows.append({
                                cleaning_log_id_column.data_column_name: uuid,
                                "question": question,
                                f"{self.cleaning_log_sheet}_value": new_val,
                                F"{self.clean_data_sheet}_value": old_val
                            })

            difference_df = pl.DataFrame(output_rows, infer_schema_length=None)

            # if there are differences found log them
            if difference_df.height > 0:
                df_to_csv(data=difference_df, filename=validation_results_filename)
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'There were {difference_df.height} differences found in the {self.cleaning_log_sheet} sheet that were not reflected in the {self.clean_data_sheet} sheet. Check the {validation_results_filename} file.'
                    ,severity = 'error'
                    ,sheet_name=self.cleaning_log_sheet
                    , details=difference_df.to_dict()
                ))

        _compare_log_to_clean(self)

        _compare_raw_to_clean_to_log(self)

        return results