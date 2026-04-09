from typing import  List

from ..validators.base import ValidationResult, BaseValidator
from ..models.schema import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData
from . config import get_pii_columns


class MandatoryColumns(BaseValidator):
    name = "MandatoryColumns"

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
        for sheet in self.schema.loaded_sheets:

            if not sheet.mandatory_columns and not sheet.unique_columns:
                continue
            
            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)
            df_columns = loaded_sheet_info.columns
            
            if sheet.mandatory_columns:
                for column in sheet.mandatory_columns:
                    if not any(map(lambda v: v in df_columns, column.combine())):
                        results.append(ValidationResult(
                            rule = self.name,
                            message = f'A column for {column.standard_name} was expexted in the {loaded_sheet_info.original_name} sheet but was not found.'
                            ,severity = 'error'
                            ,sheet_name = loaded_sheet_info.original_name
                            ))                        
            
            if sheet.unique_columns:   
                uuid_columns = sheet.unique_columns.combine()             
                if not any(map(lambda v: v in df_columns, uuid_columns)):
                    results.append(ValidationResult(
                        rule = self.name,
                        message = f'A unique column for {sheet.unique_columns.standard_name} was expexted in the {loaded_sheet_info.original_name} sheet but was not found.'
                        ,severity = 'error'
                        ,sheet_name = loaded_sheet_info.original_name
                        ))


        return results

    # polars reanames duplicate columns making this more effort 
# class DuplicateColumns(BaseValidator):
#     name = "DuplicateColumns"

#     def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
#         results: List[ValidationResult] = []

#         for _, item in data.loaded_sheets.items():
#             df_columns = item['data'].columns
#             duplicates = [column for column in set(df_columns) if df_columns.count(column) > 1]
#             if duplicates:
#                 results.append(ValidationResult(
#                         message = f'The sheet for {item['original_sheet_name']} has duplicate column names for the following columns: {duplicates}.'
#                         ,severity = 'error'
#                         ,sheet_name=item['original_sheet_name']
#                         ))
    
class UniqueColumn(BaseValidator):
    name = "UniqueColumn"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected unique columns contain any
        non unique valies across relevant sheets. 

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []        
        for sheet in self.schema.loaded_sheets:
            
            if not sheet.unique_columns:
                continue

            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)
            uuid_columns = sheet.unique_columns.combine() 
            for column in uuid_columns:
                if column in loaded_sheet_info.columns:
                    # TODO: specifiy which ids are duplicated and how many times?
                    unique_duplicated_row_count = loaded_sheet_info.data.filter(loaded_sheet_info.data.select(column).is_duplicated()).select(column).n_unique()
                    if unique_duplicated_row_count > 0:
                        results.append(ValidationResult(
                            rule = self.name,
                            message = f'For column {column} in sheet {loaded_sheet_info.mapped_name} {unique_duplicated_row_count} non unique values were found. This column should contain unique values.'
                            ,severity = 'error'
                            ,sheet_name = loaded_sheet_info.mapped_name
                            ))
                        
        return results



class PiiColumns(BaseValidator):
    name = "PiiColumns"

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

        for sheet in data.loaded_sheets:
            possible_pii_columns = [item for item in sheet.columns if item in get_pii_columns()]
            
            if possible_pii_columns:
                results.append(ValidationResult(
                            rule = self.name,
                            message = f'The sheet {sheet.original_name} has possible pii columns. Check to see if these should be removed: {possible_pii_columns}.'
                            ,severity = 'warning'
                            ,sheet_name = sheet.original_name
                            ,column_name = possible_pii_columns
                            ))
                
        return results