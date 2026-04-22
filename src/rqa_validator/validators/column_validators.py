import re
from typing import  List
import polars as pl
from ..common.file_export import df_to_csv

from ..validators.base import ValidationResult, BaseValidator
from ..models.base_dataset import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData
from . config import get_pii_columns
from ..common.list_matching import match_list_to_list
from config import settings


class MandatoryColumns(BaseValidator):

    @property
    def name(self) -> str:
        return 'MandatoryColumns'

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected mandatory columns are missing
        across relevant sheets. 

        Also checks if unique columns are missing.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []
        for sheet in self.schema.schema_loaded_sheets:

            if not sheet.mandatory_columns:
                continue
            
            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)
            if loaded_sheet_info is not None:                
                
                for column in sheet.mandatory_columns:
                    if not loaded_sheet_info.get_column_map(column.standard_name):
                        results.append(ValidationResult(
                            rule = self.name,
                            message = f'A column for {column.standard_name} was expexted in the {loaded_sheet_info.data_sheet_name} sheet but was not found.'
                            ,severity = 'error'
                            ,sheet_name = loaded_sheet_info.data_sheet_name
                            ))  
                
                
            else:
                results.append(ValidationResult(
                                rule = self.name,
                                message = f'No sheet was loaded for {sheet.standard_name}.'
                                ,severity = 'error'
                                ,sheet_name = sheet.standard_name
                                )) 


        return results
    
class UniqueColumn(BaseValidator):

    @property
    def name(self) -> str:
        return 'UniqueColumn'

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected unique columns contain any
        non unique values across relevant sheets. 

        Saves duplicates to a csv

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []   
        output_filename = 'duplicate_uuids'

        duplicated_ids_df: pl.DataFrame = pl.DataFrame([
                pl.Series("uuid",[], dtype=pl.String),
                pl.Series("sheet",[], dtype=pl.String)
            ])
            
        for sheet in self.schema.schema_loaded_sheets:

            unique_columns = sheet.get_unique_columns() 
            if not unique_columns:
                continue

            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)

            if loaded_sheet_info:
                for column in unique_columns:
                    mapped_column = loaded_sheet_info.get_column_map(column.standard_name)
                    if mapped_column is not None:
                        unique_duplicated_rows_df = loaded_sheet_info.data.filter(loaded_sheet_info.data.select(mapped_column.data_column_name).is_duplicated())\
                                                                            .select(mapped_column.data_column_name)   \
                                                                            .rename({mapped_column.data_column_name: 'uuid'})
                        unique_duplicated_row_count = unique_duplicated_rows_df.n_unique()
                        if unique_duplicated_row_count > 0:
                            # store for output
                            unique_duplicated_rows_df = unique_duplicated_rows_df.unique().with_columns(pl.lit(loaded_sheet_info.data_sheet_name).alias('sheet') ) 
                            duplicated_ids_df = pl.concat([duplicated_ids_df, unique_duplicated_rows_df])
                            results.append(ValidationResult(
                                rule = self.name,
                                message = f'For column {mapped_column.data_column_name} in sheet {loaded_sheet_info.data_sheet_name} {unique_duplicated_row_count} non unique values were found. This column should contain unique values. Check {output_filename} file for details.'
                                ,severity = 'error'
                                ,sheet_name = loaded_sheet_info.schema_sheet_name
                                , details=unique_duplicated_rows_df.to_dict()
                                ))                            

        if duplicated_ids_df.height > 0:
            df_to_csv(duplicated_ids_df, output_filename)
                        
        return results



class PiiColumns(BaseValidator):

    @property
    def name(self) -> str:
        return 'PiiColumns'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any pii columns are present
        across relevant sheets. 

        Possible pii columns are currently stored in models/config 

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []   

        pii_columns = get_pii_columns()
        for sheet in data.loaded_sheets:
            literal_matches, fuzzy_matched_values = match_list_to_list(sheet.data.columns, pii_columns, settings.FUZZY_MATCH_COLUMNS)
            
            if literal_matches:
                for item in literal_matches:
                    results.append(ValidationResult(
                                rule = self.name + ' literal comparison',
                                message = f'The sheet {sheet.data_sheet_name} has a possible pii column. Check to see if it should be removed: {item}.'
                                ,severity = 'warning'
                                ,sheet_name = sheet.data_sheet_name
                                ,column_name = item
                                ))
            if fuzzy_matched_values:
                for item in fuzzy_matched_values:
                    results.append(ValidationResult(
                                rule = self.name + ' fuzzy match comparison',
                                message = f'The sheet {sheet.data_sheet_name} has a possible pii column. Check to see if it should be removed. standard_name: {item.standard_name}, matches (matched_column, score): {item.matches} '
                                ,severity = 'warning'
                                ,sheet_name = sheet.data_sheet_name
                                ,column_name = item.standard_name
                                ))
                
        return results
    
class ColumnNameCheck(BaseValidator):
    """Check column names are variables instead of labels. 

    """
    @property
    def name(self) -> str:
        return 'ColumnNameCheck'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Check column names are variables instead of labels.

        This is done through regex matching that checks if there
        are any characters other than:
        - A-Z
        - a-z
        - 0-9
        - . or _

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: list of validation errors
        """
        results: List[ValidationResult] = [] 
        pattern = re.compile(r'[^a-zA-Z_.\d:]')

        for sheet in data.loaded_sheets:
            matches = list(filter(pattern.search, sheet.data_columns))
            if matches:

                results.append(ValidationResult(
                    rule = self.name ,
                    message = f'The sheet {sheet.data_sheet_name} has column names that appear to be labels instead of variables. Check the output for details.'
                    ,severity = 'error'
                    ,sheet_name = sheet.data_sheet_name
                    , details= {sheet.data_sheet_name: matches}
                    ))

        return results