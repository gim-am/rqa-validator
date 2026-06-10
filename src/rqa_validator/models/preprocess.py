from typing import Any

from ..common.list_matching import duplicate_list_items, lower_list_items
from ..validators.base import SeverityLevel, ValidationResult
from .base import SchemaColumnMap, SchemaSheetMap
from .base_dataset_schemas import BaseDatasetSchema


def validate_schema(schema: BaseDatasetSchema) -> list[ValidationResult]:
    """Checks that a sheet is listed only once in the schema.

    Checks that a column is listed only once per sheet. This check
    does not include unique columns as they are likely included
    in mandatory columns and only one unique column can be set

    Args:
        schema (BaseDatasetSchema): schema to validate

    Returns:
        List[ValidationResult]: validation errors
    """
    sheet_names: list[str] = []
    results: list[ValidationResult] = []

    for sheet in schema.schema_loaded_sheets:
        sheet_names.extend(sheet.combine_sheet_names())
        column_names: list[str] = sheet.combine_column_names(return_unique_list=False)

        # check duplicate columns per sheet
        duplicate_column_names = duplicate_list_items(column_names)
        if duplicate_column_names:
            results.append(
                ValidationResult(
                    rule="Duplicate column names in schema sheet",
                    message=f" Sheet {sheet} for schema {schema.dataset_type} has\
                          mandatory column standard/altername names listed on more\
                              than one column. Column names should be unique per sheet.\
                                  Check the output for details.",
                    severity=SeverityLevel.ADMIN_ERROR,
                    column_name=", ".join(duplicate_column_names),
                    details={"columns": duplicate_column_names},
                )
            )
    for sheet in schema.schema_unloaded_sheets:
        sheet_names.extend(sheet.combine_sheet_names())

    duplicate_sheet_names = duplicate_list_items(sheet_names)
    if duplicate_sheet_names:
        results.append(
            ValidationResult(
                rule="Duplicate sheet names in schema.",
                message=f"The schema for {schema.dataset_type} contains sheet names\
                      that are listed for more than one sheet. Sheet names and\
                          alternate sheet names should be unique to each schema.\
                              Check the output for details.",
                severity=SeverityLevel.ADMIN_ERROR,
                details={"sheets": duplicate_sheet_names},
            )
        )

    return results


def lowercase_schema_mappings(schema: BaseDatasetSchema) -> None:
    """lowercase and expand all sheet and column names in a schema to make
    comparisons, searches a bit easier.

    Args:
        schema (BaseDatasetSchema): schema to process
    """

    # def expand_list(str_list: list[Any]):
    #     existing_items = set(str_list)

    #     for item in str_list:
    #         if "_" in item:
    #             base_name = item.replace("_", " ")

    #             if base_name not in existing_items:
    #                 str_list.append(base_name)

    #             base_name = item.replace(" ", "")

    #             if base_name not in existing_items:
    #                 str_list.append(base_name)

    #         if " " in item:
    #             base_name = item.replace(" ", "")

    #             if base_name not in existing_items:
    #                 str_list.append(base_name)

    # def lowercase_list_strs(str_list: list[Any]) -> None:
    #     str_list[:] = [item.lower() if isinstance(item, str) else item for item in str_list]

    def process_list(str_list: list[Any]):
        lower_list_items(str_list)
        # expand_list(str_list)

    def process_sheet_mapping(sheet: SchemaSheetMap) -> None:
        if sheet.standard_name:
            sheet.standard_name = sheet.standard_name.lower()

        process_list(sheet.alternate_names)

        for column in sheet.mandatory_columns:
            process_column_mapping(column)

    def process_column_mapping(column: SchemaColumnMap | None) -> None:
        if column is None:
            return

        column.standard_name = column.standard_name.lower()

        process_list(column.alternate_names)

        if column.process_values:
            for process in column.process_values:
                process.process_name = process.process_name.lower()
                process_list(process.values)

    if schema.dataset_type:
        schema.dataset_type = schema.dataset_type.lower()

    for sheet in schema.schema_loaded_sheets:
        process_sheet_mapping(sheet)

    for sheet in schema.schema_unloaded_sheets:
        process_sheet_mapping(sheet)
