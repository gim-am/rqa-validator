
from typing import List

from ..validators.base import ValidationResult
from .schema import BaseDatasetSchema, SheetMapping, ColumnMapping

def validate_schema(schema: BaseDatasetSchema) -> List[ValidationResult]:
    """checks that a sheet is listed only once in the schema

    Args:
        schema (BaseDatasetSchema): schema to validate

    Returns:
        List[ValidationResult]: validation errors
    """
    sheet_names: List[str] = []
    # column_names: List[str] = []
    results: List[ValidationResult] = []

    for sheet in schema.schema_loaded_sheets:
        sheet_names.extend(sheet.combine_sheet_names())
        # column_names.extend(sheet.combine_column_names())

    for sheet in schema.schema_unloaded_sheets:
        sheet_names.extend(sheet.combine_sheet_names())

    duplicate_sheet_names = [item for item in set(sheet_names) if sheet_names.count(item) > 1]
    if duplicate_sheet_names:
        results.append(ValidationResult(
                rule = 'Duplicate sheet names in schema',
                message = f'The following possible sheet names were listed for more than one sheet: {duplicate_sheet_names}. Sheet names and alternate sheet names should be unique to each sheet.'
                , severity = 'admin_error'
                , sheet_name= ', '.join(duplicate_sheet_names)
            ))
        
    # duplicate_column_names = [item for item in set(column_names) if column_names.count(item) > 1]
    # if duplicate_column_names:
    #     results.append(ValidationResult(
    #             rule = 'Duplicate column names in schema',
    #             message = f'The following possible column names were listed on more than one sheet: {duplicate_column_names}.'
    #             , severity = 'admin_error'
    #             , column_name = ', '.join(duplicate_column_names)
    #         ))

    return results





def lowercase_schema_mappings(schema: BaseDatasetSchema) -> None:
    """lowercase all sheet and column names in a schema to make 
    comparisons, searches a bit easier.

    Args:
        schema (BaseDatasetSchema): schema to process
    """
    
    def lowercase_list_strs(str_list: List[str]) -> None:
        str_list[:] = list(map(str.lower, str_list))

    def process_sheet_mapping(sheet: SheetMapping) -> None:
        if sheet.standard_name:
            sheet.standard_name = sheet.standard_name.lower()
        
        lowercase_list_strs(sheet.alternate_names)
        
        for col in sheet.mandatory_columns:
            process_column_mapping(col)
        
        process_column_mapping(sheet.unique_columns)

    def process_column_mapping(col: ColumnMapping | None) -> None:
        if col is None:
            return
    
        if col.standard_name:
            col.standard_name = col.standard_name.lower()
        
        lowercase_list_strs(col.alternate_names)

    if schema.dataset_type:
        schema.dataset_type = schema.dataset_type.lower()

    for sheet in schema.schema_loaded_sheets:
        process_sheet_mapping(sheet)

    for sheet in schema.schema_unloaded_sheets:
        process_sheet_mapping(sheet)
