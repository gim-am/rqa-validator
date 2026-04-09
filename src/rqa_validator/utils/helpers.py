
from typing import List
from ..models.schema import BaseDatasetSchema, SheetMapping, ColumnMapping


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
        
        lowercase_list_strs(sheet.names)
        
        for col in sheet.mandatory_columns:
            process_column_mapping(col)
        
        process_column_mapping(sheet.unique_columns)

    def process_column_mapping(col: ColumnMapping) -> None:
        if col is None:
            return
    
        if col.standard_name:
            col.standard_name = col.standard_name.lower()
        
        lowercase_list_strs(col.names)

    if schema.dataset_type:
        schema.dataset_type = schema.dataset_type.lower()

    for sheet in schema.loaded_sheets:
        process_sheet_mapping(sheet)

    for sheet in schema.unloaded_sheets:
        process_sheet_mapping(sheet)
