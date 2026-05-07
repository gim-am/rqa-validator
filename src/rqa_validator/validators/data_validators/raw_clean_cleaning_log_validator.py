# from ...common.file_export import df_to_csv
from ...common.list_matching import filter_list, match_list
from ...common.expression_builder import create_column_difference_expression
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ..base import BaseValidator, ValidationResult, SeverityLevel
from ..helpers import (get_data_loaded_columns, 
                       get_data_loaded_sheets, 
                       get_data_sheet_ids, 
                       get_matching_id_columns, get_matching_id_columns_alt, 
                       get_schema_loaded_sheets, get_schema_process_value)


import polars as pl


from typing import List


class RawToCleanToLog(BaseValidator):
    """This process performs two steps to validate the data in the cleaning log
    
    After making sure that the required sheets and columns have been loaded and matched:

    - The first step validates that all the items in a cleaning log are reflected in the clean data.

    - The second step compares the differences between the clean and raw data sheets 
    and then checks that all these differences are reflected in the cleaning log

    The output includes:
    - items in cleaning log that have multiple updates for the same question
    - items in cleaning log where a change is recorded but old value = new value
    - questions in cleaning log that are not present in clean_data
    - items where there is a difference between cleaning_log and clean_data values
    - items where there is a difference between raw_data/clean_data and the cleaning log

    """
    def __init__(self, schema: BaseDatasetSchema,
                 clean_data_sheet:str = 'clean_data',
                 raw_data_sheet: str = 'raw_data',
                 cleaning_log_sheet: str | None = 'cleaning_log',
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
        return 'RawToCleanToLog'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """This process compares the differences between the clean and raw data sheets 
        and then checks that all these differences are reflected in the cleaning log if provided

        The output includes:
        - items where there is a difference between raw_data/clean_data and the cleaning log
        - if no cleaning log is provided then an error is returned if there are differences between raw and clean

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        # multiple_changes_filename = 'cleaning_log_validation_multiple_changes'
        # validation_results_filename = 'cleaning_log_validation_results'

        # PRE-VALIDATION - check sheets, columns etc all exist

        sheet_names = [self.clean_data_sheet, self.raw_data_sheet]
        if self.cleaning_log_sheet is not None:
            sheet_names.append(self.cleaning_log_sheet )

        result, data_loaded_sheets = get_data_loaded_sheets(data=data, 
                                                       sheet_names=sheet_names,
                                                        rule=self.name)

        if result:
            results.extend(result)
            return results
        
        result, data_sheet_ids = get_data_sheet_ids(schema=self.schema, 
                                                       data = {self.clean_data_sheet: data_loaded_sheets[self.clean_data_sheet],
                                                               self.raw_data_sheet: data_loaded_sheets[self.raw_data_sheet]},
                                                        rule=self.name)

        if result:
            results.extend(result)
            return results
        
        result, raw_to_clean_matching_id_columns = get_matching_id_columns(data_sheet_ids[self.raw_data_sheet], self.raw_data_sheet, data_loaded_sheets[self.clean_data_sheet] .column_map, self.clean_data_sheet, self.name)
        if result is not None:
            results.append(result)
            return results
        
        assert raw_to_clean_matching_id_columns is not None  
        raw_data_id_columns = raw_to_clean_matching_id_columns[0][0]
        
        if self.cleaning_log_sheet is None:
            clean_data_id_columns = raw_to_clean_matching_id_columns[0][1]
        else:
            result, clean_to_log_matching_id_columns = get_matching_id_columns(data_sheet_ids[self.clean_data_sheet], self.clean_data_sheet, data_loaded_sheets[self.cleaning_log_sheet].column_map, self.cleaning_log_sheet, self.name)
            if result is not None:
                result, clean_data_id_columns, clean_log_id_columns = get_matching_id_columns_alt(data_sheet_ids[self.clean_data_sheet], self.clean_data_sheet, data_loaded_sheets[self.cleaning_log_sheet].column_map, self.cleaning_log_sheet, self.name)
                if result is not None:
                    results.append(result)
                    return results
                else:
                    clean_data_id_columns = clean_data_id_columns[0]
                    clean_log_id_columns = clean_log_id_columns[0]
            else:
                clean_data_id_columns = clean_to_log_matching_id_columns[0][0]
                clean_log_id_columns = clean_to_log_matching_id_columns[0][1]
        
            result, data_loaded_columns = get_data_loaded_columns(data = {self.cleaning_log_new_value_column: data_loaded_sheets[self.cleaning_log_sheet],
                                                                        self.cleaning_log_old_value_column: data_loaded_sheets[self.cleaning_log_sheet],
                                                                        self.cleaning_log_question_column: data_loaded_sheets[self.cleaning_log_sheet],
                                                                        self.cleaning_log_change_type_column: data_loaded_sheets[self.cleaning_log_sheet],
                                                                        #   clean_log_id_columns.schema_column_name: data_loaded_sheets[self.cleaning_log_sheet],
                                                                        },
                                                            rule=self.name)

            if result:
                results.extend(result)
                return results
            
            result, schema_loaded_sheets = get_schema_loaded_sheets(schema=self.schema, 
                                                        sheet_names=[self.cleaning_log_sheet],
                                                            rule=self.name)
            if result:
                results.extend(result)
                return results

            schema_change_type_column = schema_loaded_sheets[self.cleaning_log_sheet].get_column(self.cleaning_log_change_type_column)
            if schema_change_type_column is None:
                # this should already have been validated when checking mandatory columns
                return results
        
            result, schema_change_type_values = get_schema_process_value(self.process_value_map_name, self.cleaning_log_sheet, schema_change_type_column, self.name)
            if result is not None:
                results.append(result)
                return results
            
            assert schema_change_type_values is not None  
        

        # TRANSFORMATION: transforms data in preparation for comparison   
         # dataframe of actual changes made
            modified_rows_df = data_loaded_sheets[self.cleaning_log_sheet].data.filter(pl.col(data_loaded_columns[self.cleaning_log_change_type_column].data_column_name) \
                                                                        .str.to_lowercase().is_in(schema_change_type_values.values) ) \
                                                            .select([clean_log_id_columns.data_column_name,
                                                                        data_loaded_columns[self.cleaning_log_new_value_column].data_column_name,
                                                                        data_loaded_columns[self.cleaning_log_old_value_column].data_column_name,
                                                                        data_loaded_columns[self.cleaning_log_change_type_column].data_column_name,
                                                                        data_loaded_columns[self.cleaning_log_question_column].data_column_name])
        
        # Gets the difference between raw and clean sheets and compares 
        # this to the cleaning log
        # get columns that are in both clean and raw sheets
        # then filter the sheets
        clean_data_columns = filter_list(match_list(data_loaded_sheets[self.clean_data_sheet] .data.columns, 
                                                            data_loaded_sheets[self.raw_data_sheet] .data.columns), 
                                        [clean_data_id_columns.data_column_name])
                                        
        clean_data_filtered_df = data_loaded_sheets[self.clean_data_sheet] .data.select([clean_data_id_columns.data_column_name] + clean_data_columns)
        raw_data_filtered_df = data_loaded_sheets[self.raw_data_sheet] .data.select([raw_data_id_columns.data_column_name] + clean_data_columns) \
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
                            f"{self.cleaning_log_question_column}": question,
                            f"{self.cleaning_log_old_value_column}": str(old_val),
                            F"{self.cleaning_log_new_value_column}": str(new_val)
                        })
            # difference between raw and clean
            difference_raw_to_clean_df = pl.DataFrame(output_rows, infer_schema_length=None)

            # difference between above and cleaning log
            if self.cleaning_log_sheet is not None:
                difference_df = difference_raw_to_clean_df.join(other=modified_rows_df,
                                                                how='anti',
                                                                left_on='uuid',
                                                                right_on=clean_log_id_columns.data_column_name)
                
                if difference_df.height > 0:
                    # df_to_csv(data=difference_df, filename=validation_results_filename)
                    results.append(ValidationResult(
                        rule = self.name,
                        message = f'There were {difference_df.height} differences found in the {self.clean_data_sheet} sheet that were not reflected in the {self.cleaning_log_sheet} sheet. Check the output for details.'
                        ,severity = SeverityLevel.ERROR
                        ,sheet_name=self.cleaning_log_sheet
                        , details=difference_df.to_dict()
                    ))    
            else:
                results.append(ValidationResult(
                        rule = self.name,
                        message = f'There were {difference_raw_to_clean_df.height} differences found between the {self.clean_data_sheet} sheet and the {self.raw_data_sheet} but no cleaning log was found. Check the output for details.'
                        ,severity = SeverityLevel.ERROR
                        ,sheet_name=self.cleaning_log_sheet
                        , details=difference_raw_to_clean_df.to_dict()
                    ))    



        return results