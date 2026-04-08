from typing import  List

from ..validators.base import ValidationResult, BaseValidator
from ..models.schema import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData
from ..models import config as conf


class MandatoryColumns(BaseValidator):
    name = "MandatoryColumns"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected mandatory columns are missing
        across relevant sheets. 

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []
        for sheet in self.schema.loaded_sheets:
            # a basic non check does not work for ColumnMapping class
            # so check if there is actually data
            uuid_columns = sheet.unique_uuid_column.combine()
            if not sheet.mandatory_columns and not uuid_columns:
                continue
            
            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)
            df_columns = loaded_sheet_info.data.columns
            
            if sheet.mandatory_columns:
                for column in sheet.mandatory_columns:
                    if not any(map(lambda v: v in df_columns, column.combine())):
                        results.append(ValidationResult(
                            message = f'A column for {column.standard_name} was expexted in the {loaded_sheet_info.original_name} sheet but was not found.'
                            ,severity = 'error'
                            ,sheet_name = loaded_sheet_info.original_name
                            ))
                        
            
            if uuid_columns:                
                if not any(map(lambda v: v in df_columns, uuid_columns)):
                    results.append(ValidationResult(
                        message = f'A unique column for {sheet.unique_uuid_column.standard_name} was expexted in the {loaded_sheet_info.original_name} sheet but was not found.'
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

            uuid_columns = sheet.unique_uuid_column.combine() 
            if not uuid_columns:
                continue

            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)

            df = loaded_sheet_info.data
            df_columns = df.columns
            for column in uuid_columns:
                if column in df_columns:
                    # TODO: specifiy which ids are duplicated and how many times?
                    unique_duplicated_row_count = df.filter(df.select(column).is_duplicated()).select(column).n_unique()
                    if unique_duplicated_row_count > 0:
                        results.append(ValidationResult(
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
            possible_pii_columns = [item for item in sheet.data.columns if item in conf.PII_COLUMN_NAMES]
            
            if possible_pii_columns:
                results.append(ValidationResult(
                            message = f'The sheet {sheet.original_name} has possible pii columns. Check to see if these should be removed: {possible_pii_columns}.'
                            ,severity = 'warning'
                            ,sheet_name = sheet.original_name
                            ,column_name = possible_pii_columns
                            ))
                
        return results