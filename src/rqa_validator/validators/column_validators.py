from typing import  List
from polars import DataFrame

from ..validators.base import ValidationResult, BaseValidator
from ..models.schema import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData



class MandatoryColumns(BaseValidator):
    name = "MandatoryColumns"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        for sheet in self.schema.loaded_sheets:
            if not sheet.mandatory_columns:
                continue

            df_columns = data.loaded_sheets[sheet.standard_name]['data'].columns
            for column in sheet.mandatory_columns:
                if not any(map(lambda v: v in df_columns, column.combine())):
                    results.append(ValidationResult(
                        message=f'A column for {column.standard_name} was expexted in the {data.loaded_sheets[sheet.standard_name]['original_sheet_name']} sheet but was not found.'
                        ,severity='error'
                        ,sheet_name=data.loaded_sheets[sheet.standard_name]['original_sheet_name']
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
#                         message=f'The sheet for {item['original_sheet_name']} has duplicate column names for the following columns: {duplicates}.'
#                         ,severity='error'
#                         ,sheet_name=item['original_sheet_name']
#                         ))
    
class UniqueColumn(BaseValidator):
    name = "UniqueColumn"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        results: List[ValidationResult] = []        
        for sheet in self.schema.loaded_sheets:
            
            if not sheet.unique_uuid:
                continue
            
            uuid_columns = sheet.unique_uuid_column.combine() 
            if not uuid_columns:
                results.append(ValidationResult(
                        message=f'Admin warning: The schema for {sheet.standard_name} states unique uuids are required but no column names are provided. Check that the schema is correct.'
                        ,severity='warning'
                        ,sheet_name=data.loaded_sheets[sheet.standard_name]['original_sheet_name']
                        ))
                continue

            df: DataFrame = data.loaded_sheets[sheet.standard_name]['data']
            df_columns = df.columns
            for column in uuid_columns:
                if column in df_columns:
                    # TODO: specifiy which ids are duplicated and how many times?
                    unique_duplicated_row_count = df.filter(df.select(column).is_duplicated()).select(column).n_unique()
                    if unique_duplicated_row_count > 0:
                        results.append(ValidationResult(
                            message=f'For column {column} {unique_duplicated_row_count} in sheet {data.loaded_sheets[sheet.standard_name]['original_sheet_name']} non unique values were found. This column should contain unique values.'
                            ,severity='error'
                            ,sheet_name=data.loaded_sheets[sheet.standard_name]['original_sheet_name']
                            ))
                        
        return results



