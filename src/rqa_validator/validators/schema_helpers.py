from ..models.base import ProcessValueMap, SchemaColumnMap, SchemaSheetMap
from ..models.base_dataset import BaseDatasetSchema
from ..validators.base import SeverityLevel, ValidationResult


def get_schema_id_column(
    source: SchemaSheetMap, rule: str
) -> tuple[ValidationResult | None, list[SchemaColumnMap]]:
    """Gets unique columns for a schema sheet

    Args:
        source (SchemaSheetMap): Sheet to search
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, List[SchemaColumnMap]]: validation results,
            unique columns if found
    """
    result = None
    matching_columns = source.get_unique_columns()
    if len(matching_columns) != 1:
        result = ValidationResult(
            rule=rule,
            message=f"Expected 1 ID column for sheet '{source.standard_name}' but"
            f" {len(matching_columns)} were found.",
            severity=SeverityLevel.ERROR,
        )
    if result is None:
        assert matching_columns is not None

    return result, matching_columns


def get_schema_process_value(
    process_value_map_name: str,
    sheet_name: str,
    schema_column: SchemaColumnMap,
    rule: str,
) -> tuple[ValidationResult | None, ProcessValueMap | None]:
    """Gets schema process values if found

    Args:
        process_value_map_name (str): name of process
        sheet_name (str): sheet name
        schema_column (ColumnMapping): schema column that process is linked to
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, ProcessValueMap | None]: validation errors if any
            , process values if found
    """

    result = None

    process_values = schema_column.get_process_values(process_value_map_name)

    if process_values is None or len(process_values.values) == 0:
        result = ValidationResult(
            rule=rule,
            message="process_values were expected for column "
            f" '{schema_column.standard_name}' for process '{process_value_map_name}'.",
            severity=SeverityLevel.ERROR,
            sheet_name=sheet_name,
            column_name=schema_column.standard_name,
        )
    else:
        assert process_values is not None

    return result, process_values


def get_schema_process_values(
    data: dict[str, dict[str, SchemaColumnMap]], rule: str
) -> tuple[list[ValidationResult], dict[str, ProcessValueMap]]:
    """Gets a list of schema process values if found.


    Args:
        data (dict[str, dict[str, ColumnMapping]]): sheet name,
             [process value name, schema column]
        rule (str): validation rule

    Returns:
        tuple[List[ValidationResult], dict[str, ProcessValueMap]]: validation errors if
             any, process value name, process values if found
    """
    results: list[ValidationResult] = []
    process_values: dict[str, ProcessValueMap] = {}

    for sheet, item in data.items():
        for process, column in item.items():
            result, process_value = get_schema_process_value(process, sheet, column, rule)

            if result is None:
                assert process_value is not None
                process_values[process] = process_value
            else:
                results.append(result)

    return results, process_values


def get_schema_loaded_column(
    loaded_sheet: SchemaSheetMap, column: str, rule: str
) -> tuple[ValidationResult | None, SchemaColumnMap | None]:
    """Gets a schema column if it exists.

    Args:
        loaded_sheet (SheetMapping): loaded schema sheet containing the column
        column (str): column to find
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, ColumnMapping | None]: validation errors if any,
          loaded column
    """
    result = None

    schema_column = loaded_sheet.get_column(column)

    if schema_column is None:
        # should not actually happen as its already mapped above.
        result = ValidationResult(
            rule=rule,
            message=f"A column for '{column}' in schema sheet "
            f" '{loaded_sheet.standard_name}' is expected.",
            severity=SeverityLevel.ERROR,
            sheet_name=loaded_sheet.standard_name,
            column_name=column,
        )
    return result, schema_column


def get_schema_loaded_columns(
    data: dict[str, SchemaSheetMap], rule: str
) -> tuple[list[ValidationResult], dict[str, SchemaColumnMap]]:
    """Gets a list of schema columns if they exists

    Args:
        data (dict[str, SheetMapping]): column name, loaded schema sheet
        rule (str): validation rule

    Returns:
        tuple[List[ValidationResult], dict[str, ColumnMapping]]: list of validation
             errors if any, column and schema column map
    """

    results: list[ValidationResult] = []
    loaded_columns: dict[str, SchemaColumnMap] = {}

    for column, sheet in data.items():
        result, schema_column = get_schema_loaded_column(sheet, column, rule)
        if result is None:
            assert schema_column is not None
            loaded_columns[column] = schema_column
        else:
            results.append(result)

    return results, loaded_columns


def get_schema_loaded_sheet(
    schema: BaseDatasetSchema, sheet_name: str, rule: str
) -> tuple[ValidationResult | None, SchemaSheetMap | None]:
    """Gets a schema loaded sheet if it exists.

    Args:
        schema (BaseDatasetSchema): dataset scheema
        sheet_name (str): name of sheet to load
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, SheetMapping | None]: validation error if any,
             loaded sheet if found
    """
    result = None
    schema_sheet = schema.get_schema_loaded_sheet(sheet_name=sheet_name)

    if not schema_sheet:
        result = ValidationResult(
            rule=rule,
            message=f"A schema sheet for '{sheet_name}' is expected.",
            severity=SeverityLevel.ERROR,
            sheet_name=sheet_name,
        )

    return result, schema_sheet


def get_schema_loaded_sheets(
    schema: BaseDatasetSchema, sheet_names: list[str], rule: str
) -> tuple[list[ValidationResult], dict[str, SchemaSheetMap]]:
    """Gets a list of schema loaded sheets if it exists.

    Args:
        schema (BaseDatasetSchema): dataset scheema
        sheet_names (List[str]): list of names of sheets to load
        rule (str): validation rule

    Returns:
        tuple[List[ValidationResult], dict[str, SheetMapping]]: list of validation
             errors if any,  dictionary of sheet names and loaded sheets if found
    """
    results: list[ValidationResult] = []
    loaded_sheets: dict[str, SchemaSheetMap] = {}

    for sheet in sheet_names:
        result, loaded_sheet = get_schema_loaded_sheet(schema, sheet, rule)

        if result is None:
            assert loaded_sheet is not None
            loaded_sheets[sheet] = loaded_sheet
        else:
            results.append(result)

    return results, loaded_sheets
