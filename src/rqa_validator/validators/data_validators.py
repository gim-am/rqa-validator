from typing import  List
import polars as pl

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
            for column in loaded_sheet.data.columns:

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
            has_nan = pl.any_horizontal([pl.col(f"is_{column}_nan_value") for column in loaded_sheet.data.columns])
            nan_only_df = nan_df.filter(has_nan)

            output_rows = []

            # create df of only invalid data
            if not nan_only_df.is_empty():
                for row in nan_only_df.iter_rows(named=True):
                    uuid = row[id_column.data_column_name]
                    for column in loaded_sheet.data.columns:
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


    