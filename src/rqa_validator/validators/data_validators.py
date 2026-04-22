from typing import  List
import polars as pl

from ..common.file_export import df_to_csv
from ..common.list_matching import  filter_list, match_sheet_columns
from ..common.schema_matching import get_matching_unique_columns
from ..models.base_dataset import BaseDatasetSchema
from ..validators.base import ValidationResult, BaseValidator
from ..loaders.excel_loader import ExcelLoaderData
from config import settings


class ConsentCheck(BaseValidator):
    """Checks that records in raw_data that did not provide consent are
    not present in clean_data"""
    def __init__(self,
                 schema: BaseDatasetSchema,
                 raw_data_sheet: str = 'raw_data',
                 clean_data_sheet: str = 'clean_data',
                 schema_consent_column = 'consent') -> None:
        """
        Args:
            schema (BaseDatasetSchema): dataset schema
            raw_data_sheet (str, optional): schema raw_data sheet name. Defaults to 'raw_data'.
            clean_data_sheet (str, optional): shema clean_data sheet name. Defaults to 'clean_data'.
            schema_consent_column (str, optional): column in raw_data that gives consent value. Defaults to 'consent'.
        """
        self.raw_data_sheet = raw_data_sheet
        self.clean_data_sheet = clean_data_sheet
        self.schema = schema
        self.schema_consent_column = schema_consent_column
        self.process_value_map_name = 'consent_check_validation'

    @property
    def name(self) -> str:
        return 'ConsentCheck'
    
    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks that records in raw_data that did not provide consent are
        not present in clean_data.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        
        loaded_raw_data_sheet = data.get_loaded_sheet(self.raw_data_sheet)
            
        if loaded_raw_data_sheet is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'An excel sheet for {self.raw_data_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.raw_data_sheet
            ))  
            return results 
        
        loaded_clean_data_sheet = data.get_loaded_sheet(self.clean_data_sheet)

        if loaded_clean_data_sheet is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'An excel sheet for {self.clean_data_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.clean_data_sheet
            ))  
            return results 

        consent_column = loaded_raw_data_sheet.get_column_map(self.schema_consent_column)

        if consent_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.schema_consent_column} in excel sheet {loaded_raw_data_sheet.data_sheet_name} is expected.'
                ,severity = 'error'
                ,sheet_name=loaded_raw_data_sheet.data_sheet_name
            ))  
            return results 

        schema_sheet = self.schema.get_schema_loaded_sheet(self.raw_data_sheet)
        
        if schema_sheet is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A schema sheet for {self.raw_data_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.raw_data_sheet
            ))  
            return results 
        
        schema_consent_column = schema_sheet.get_column(consent_column.schema_column_name)

        if schema_consent_column is None:
            # should not actually happen as its already mapped above.
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {consent_column.schema_column_name} in schema sheet {self.raw_data_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.raw_data_sheet
            ))  
            return results 
        
        consent_values = schema_consent_column.get_process_values(self.process_value_map_name)

        if consent_values is None or len(consent_values.values) == 0:
            results.append(ValidationResult(
            rule = self.name,
            message = f'process_values were expected for column {consent_column.schema_column_name} for process {self.process_value_map_name}.'
            ,severity = 'error'
            , sheet_name= self.raw_data_sheet
            , column_name=consent_column.schema_column_name
            ))  
            return results 
        
        # get id column for the output dataframe
        raw_data_id_column = get_matching_unique_columns(schema=self.schema,
                                            loaded_data=loaded_raw_data_sheet, 
                                            sheet_name=self.raw_data_sheet)

        if len(raw_data_id_column) != 1:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A single unique column for schema sheet {self.raw_data_sheet} and matching excel sheet {loaded_raw_data_sheet.data_sheet_name} was expected.'
                ,severity = 'error'
                ,sheet_name=self.raw_data_sheet
            ))  
            return results 
        
        clean_data_id_column = get_matching_unique_columns(schema=self.schema,
                                            loaded_data=loaded_clean_data_sheet, 
                                            sheet_name=self.clean_data_sheet)

        if len(clean_data_id_column) != 1:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A single unique column for schema sheet {self.clean_data_sheet} and matching excel sheet {loaded_clean_data_sheet.data_sheet_name} was expected.'
                ,severity = 'error'
                ,sheet_name=self.clean_data_sheet
            ))  
            return results 
        
        raw_data_id_column = raw_data_id_column[0]
        clean_data_id_column = clean_data_id_column[0]
    
        # get records that have not provided consent
        raw_data_filter_df = loaded_raw_data_sheet.data.filter(~pl.col(consent_column.data_column_name).str.to_lowercase()
                                                .is_in(consent_values.values)) \
                                        .select([raw_data_id_column.data_column_name, consent_column.data_column_name])

        if raw_data_filter_df.height > 0:
            # join to clean_data to see if clean_data contains any of the records
            clean_data_filter_df = loaded_clean_data_sheet.data.join(other=raw_data_filter_df,
                                                                     left_on=clean_data_id_column.data_column_name,
                                                                     right_on=raw_data_id_column.data_column_name,
                                                                     how='inner')
            if clean_data_filter_df.height > 0:
                results.append(ValidationResult(
                rule = self.name,
                message = f'There were {clean_data_filter_df.height} row/s in {loaded_clean_data_sheet.data_sheet_name} that did not provide consent. Check the output results for details.'
                ,severity = 'error'
                ,details=clean_data_filter_df.select([clean_data_id_column.data_column_name]).to_dict()
            ))                                

        return results


class NaNCheck(BaseValidator):
    """Checks columns for invalid numeric values like NaN and -999.
    Invalid values are stored in the config file.

    """
    def __init__(self,
                 schema: BaseDatasetSchema,
                 sheets: List[str] = ['clean_data']) -> None:
        """
        Args:
            schema (BaseDatasetSchema): schema for the dataset
            sheets (List[str], optional): list of sheets to be checked. Defaults to ['clean_data'].
        """
        self.sheets = sheets
        self.schema = schema

    @property
    def name(self) -> str:
        return 'NaNCheck'
    
    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks columns for invalid numeric values like NaN and -999.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        output_difference_df =  pl.DataFrame([
                pl.Series("uuid",[], dtype=pl.String),
                pl.Series("sheet",[], dtype=pl.String),
                pl.Series("column",[], dtype=pl.String),
                pl.Series("value",[], dtype=pl.String)
            ])

        for sheet in self.sheets:
            loaded_sheet = data.get_loaded_sheet(sheet)
                
            if loaded_sheet is None:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A sheet for {sheet} is expected.'
                    ,severity = 'error'
                    ,sheet_name=sheet
                ))  
                continue
            
            # get id column for the output dataframe
            id_column = get_matching_unique_columns(schema=self.schema,
                                              loaded_data=loaded_sheet, 
                                              sheet_name=sheet)

            if len(id_column) != 1:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A single unique column for schema sheet {sheet} and matching excel sheet {loaded_sheet.data_sheet_name} was expected.'
                    ,severity = 'error'
                    ,sheet_name=sheet
                ))  
                continue

            id_column = id_column[0]

            nan_value_expressions = []

            # build expression to find possible invalid values or NaNs
            for column in loaded_sheet.data_columns:

                expression = pl.any_horizontal(
                    (
                        (pl.col(column).is_nan() | (pl.col(column).is_in( settings.NANCHECK_NUMERIC_VALUES))) if loaded_sheet.data.schema[column].is_float() else False 
                        | (pl.col(column).is_in( settings.NANCHECK_NUMERIC_VALUES) ) if loaded_sheet.data.schema[column].is_integer() else False
                        | (pl.col(column).is_in( settings.NANCHECK_STRING_VALUES) ) if loaded_sheet.data.schema[column] == pl.String else pl.lit(False)
                        
                    ).alias(f"is_{column}_nan_value")

                )
                nan_value_expressions.append(expression)
            
            # get a df that has nan/invalid data in a row
            nan_df = loaded_sheet.data.with_columns(nan_value_expressions)
            has_nan = pl.any_horizontal([pl.col(f"is_{column}_nan_value") for column in loaded_sheet.data_columns])
            nan_only_df = nan_df.filter(has_nan)

            output_rows = []

            # create df of only invalid data
            if not nan_only_df.is_empty():
                for row in nan_only_df.iter_rows(named=True):
                    uuid = row[id_column.data_column_name]
                    for column in loaded_sheet.data_columns:
                        is_changed = row[f"is_{column}_nan_value"]
                        
                        if is_changed:
                            value = row[column]
                            # new_val = row[new_col]
                            output_rows.append({
                                "uuid": uuid,
                                "sheet": sheet,
                                "column": column,
                                "value": str(value),
                            })
                output_difference_df = pl.concat([output_difference_df, 
                                                        pl.DataFrame(output_rows, infer_schema_length=None)])


        if output_difference_df.height > 0:
            # df_to_csv(data=difference_df, filename=validation_results_filename)
            results.append(ValidationResult(
                rule = self.name,
                message = f'There were {output_difference_df.height} possible invalid values found. Check the output results for details.'
                ,severity = 'error'
                ,details=output_difference_df.to_dict()
            ))  

        return results


class CleaningLog(BaseValidator):
    """Validates that the items in a cleaning log are reflected in the clean data.

    This process:
    - makes sure the required sheets and columns have been loaded and matched
    - filters the cleaning log to have only rows that have a changed value
    - does some transformations and comparisons between clean_data and the cleaning_log 
    - outputs items where there is a difference between cleaning_log and clean_data

    """
    def __init__(self, schema: BaseDatasetSchema, 
                 clean_data_sheet:str = 'clean_data',
                 cleaning_log_sheet: str = 'cleaning_log',
                 cleaning_log_new_value_column:str = 'new_value', 
                 cleaning_log_old_value_column:str = 'old_value', 
                 cleaning_log_question_column:str = 'question',
                 cleaning_log_change_type_column:str = 'change_type') -> None:
        """Validates that the items in a cleaning log are reflected in the clean data

        Args:
            schema (BaseDatasetSchema): dataset schema for the dataset
            clean_data_sheet (str, optional): name of the clean data sheet. Defaults to 'clean_data'.
            cleaning_log_sheet (str, optional): name of the cleaning log sheet. Defaults to 'cleaning_log'.
            cleaning_log_new_value_column (str, optional): name of the cleaning log new value column. Defaults to 'new_value'.
            cleaning_log_question_column (str, optional): name of the cleaning log quesitons column. Defaults to 'question'.
            cleaning_log_change_type_column (str, optional): name of the cleaning log change_type column. Defaults to 'change_type'
        """
        self.schema = schema
        self.clean_data_sheet = clean_data_sheet
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
        """Validates that the items in a cleaning log are reflected in the clean data.

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
        new_value_column = cleaning_log_loaded_sheet.get_column_map(self.cleaning_log_new_value_column)
        if new_value_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.cleaning_log_new_value_column} is expected.'
                ,severity = 'error'
                , sheet_name= self.cleaning_log_sheet
            ))  
            return results 
        
        old_value_column = cleaning_log_loaded_sheet.get_column_map(self.cleaning_log_old_value_column)
        if old_value_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.cleaning_log_old_value_column} is expected.'
                ,severity = 'error'
                , sheet_name= self.cleaning_log_sheet
            ))  
            return results 

        question_column = cleaning_log_loaded_sheet.get_column_map(self.cleaning_log_question_column)
        if question_column is None:    
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

        matching_id_columns = match_sheet_columns(clean_data_sheet_ids, cleaning_log_loaded_sheet.column_map)
        # should only be one matching id column between the sheets.
        if len(matching_id_columns) != 1:
            results.append(ValidationResult(
                rule = self.name,
                message = f'Expected 1 linkable ID column for sheets {self.clean_data_sheet} and {self.cleaning_log_sheet} but {len(matching_id_columns)} were found.'
                ,severity = 'error'
            ))  
            return results  
        
        clean_data_id_columns = matching_id_columns[0]
        cleaning_log_id_column = cleaning_log_loaded_sheet.get_column_map(clean_data_id_columns.schema_column_name)

        if cleaning_log_id_column is None:
            # should not happen as it was just matched/checked
            results.append(ValidationResult(
                rule = self.name,
                message = f'Expected to find a column for {clean_data_id_columns.schema_column_name} in sheet {self.cleaning_log_sheet} but none was found.'
                ,severity = 'error'
            ))  
            return results  
        
        # TRANSFORMATION: transforms data in preparation for comparison

        


        # dataframe of actual changes made
        modified_rows_df = cleaning_log_loaded_sheet.data.filter(pl.col(cleaning_log_change_type_column.data_column_name) \
                                                                 .str.to_lowercase().is_in(schema_change_type_values.values) ) \
                                                        .select([cleaning_log_id_column.data_column_name,
                                                                  new_value_column.data_column_name,
                                                                  old_value_column.data_column_name,
                                                                  cleaning_log_change_type_column.data_column_name,
                                                                  question_column.data_column_name]) 
                                                                    
        # racods where the same question was updated more than once for the same id
        multiple_change_mask = modified_rows_df.select(cleaning_log_id_column.data_column_name, 
                                                       question_column.data_column_name, 
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
        same_value_df = modified_rows_df.filter(pl.col(new_value_column.data_column_name).cast(pl.Utf8) == pl.col(old_value_column.data_column_name).cast(pl.Utf8)) \
                                                        .select(cleaning_log_id_column.data_column_name,
                                                                new_value_column.data_column_name,
                                                                old_value_column.data_column_name,
                                                                cleaning_log_change_type_column.data_column_name)
        if same_value_df.height > 0:
            results.append(ValidationResult(
                rule = self.name,
                message = f'{same_value_df.height} row/s had {old_value_column.data_column_name} equal {new_value_column.data_column_name}. Check the output file {multiple_changes_filename} for details.'
                ,severity = 'warning'
                ,details = same_value_df.to_dict()
            ))  

        # remove records with multiple chages as there is no way to determine which should
        # be the most recent
        unique_modified_rows_df = modified_rows_df.filter(~multiple_change_mask).sort(cleaning_log_id_column.data_column_name)
        
        if unique_modified_rows_df.height < 1:
            return results
        # get a list of questions that had values changed
        questions = unique_modified_rows_df.select(question_column.data_column_name).unique().to_series().str.to_lowercase().to_list()

        missing_quesitons = filter_list(questions, clean_data_loaded_sheet.data_columns)
        if missing_quesitons:
            results.append(ValidationResult(
                rule = self.name,
                message = f'The following questions are listed in {cleaning_log_loaded_sheet.data_sheet_name} but were not found in {clean_data_loaded_sheet.data_sheet_name}: {missing_quesitons}.'
                ,severity = 'Error'
            ))  
            return results

        # add column to specifiy an update. this helps to specify which
        # questions were updated later after the pivot as the pivot will
        # add a column for each question even if that question was not updated
        # for a particular uuid. 
        # The result of this will be that question columns
        # that actually had an update in cleaning log will have 'true' for that question
        # while all other other questions will be null
        # fill null with '' to make comparison easier later
        unique_modified_rows_df = unique_modified_rows_df.with_columns(pl.lit(True).alias('is_update')) \
                                                        .with_columns(pl.col(new_value_column.data_column_name).fill_null(''))
        
        # pivot the table for use later. lower the questions/column names.
        unique_modified_rows_df = unique_modified_rows_df.pivot(on=question_column.data_column_name,
                                                      index=cleaning_log_id_column.data_column_name, 
                                                      values=[new_value_column.data_column_name, 'is_update']) \
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
                                                                .fill_null('')
        # join dataframes so columns can be matched below
        joined_df = unique_modified_rows_df.join(clean_data_filtered_df,
                                                 left_on=cleaning_log_id_column.data_column_name,
                                                 right_on=clean_data_id_columns.data_column_name,
                                                 how='left')      
          
        # COMPARISONS: compares data to look for differences

        # build expressions to check for differences in the two dataframes
        difference_expressions = []
        for question in questions:
            new_col = f"{question}_val"
            col_has_update = f"{question}_has_update"
            # Check if the new value exists AND is different from the old value
            # cast to string to ensure comparison between int and str if types differ
            diff_expr = (
                (pl.col(col_has_update).is_not_null()) &
                (pl.col(question).cast(pl.Utf8) != pl.col(new_col).cast(pl.Utf8))
            ).alias(f"is_{question}_changed")
            
            difference_expressions.append(diff_expr)

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

        return results
    