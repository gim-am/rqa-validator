from ..common.list_matching import match_sheet_columns, match_sheet_columns_ids
from ..common.schema_matching import get_matching_unique_columns
from ..loaders.base import DataColumnMap, DataSheetMap
from ..loaders.excel_loader import ExcelLoaderData
from ..models.base import ProcessValueMap, SchemaColumnMap, SchemaSheetMap
from ..models.base_dataset import BaseDatasetSchema
from .base import SeverityLevel, ValidationResult


def get_data_loaded_sheet(
    data: ExcelLoaderData, sheet_name: str, rule: str
) -> tuple[ValidationResult | None, DataSheetMap | None]:
    """Gets a data loaded sheet if it exists.

    Args:
        data (ExcelLoaderData): excel data
        sheet_name (str): name of sheet to load
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, SheetMap | None]: validation error if any,
             loaded sheet if found
    """
    result = None
    loaded_sheet = data.get_loaded_sheet(sheet_name=sheet_name)

    if loaded_sheet is None:
        result = ValidationResult(
            rule=rule,
            message=f"An excel sheet for '{sheet_name}' is expected.",
            severity=SeverityLevel.ERROR,
            sheet_name=sheet_name,
        )

    return result, loaded_sheet


def get_data_loaded_sheets(
    data: ExcelLoaderData, sheet_names: list[str], rule: str
) -> tuple[list[ValidationResult], dict[str, DataSheetMap]]:
    """Gets a list of data loaded sheets if they exist.

    Args:
        data (ExcelLoaderData): excel data
        sheet_names (List[str]): list of sheet names to load
        rule (str): validation rule

    Returns:
        tuple[List[ValidationResult], dict[str, SheetMap]]:  list of validation errors
             if any, dictionary of sheet names and loaded sheets if found
    """
    results: list[ValidationResult] = []
    loaded_sheets: dict[str, DataSheetMap] = {}

    for sheet in sheet_names:
        result, loaded_sheet = get_data_loaded_sheet(data, sheet, rule)

        if result is None:
            assert loaded_sheet is not None
            loaded_sheets[sheet] = loaded_sheet
        else:
            results.append(result)

    return results, loaded_sheets


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


def get_data_loaded_column(
    loaded_sheet: DataSheetMap, column_name: str, rule: str
) -> tuple[ValidationResult | None, DataColumnMap | None]:
    """Gets a data loaded column if found.

    Args:
        loaded_sheet (SheetMap): sheet the column is on
        column_name (str): name of the column to find
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, ColumnMap | None]: validation error if any,
             loaded column if found
    """
    result = None

    column = loaded_sheet.get_column_map(column_name)
    if column is None:
        result = ValidationResult(
            rule=rule,
            message=f"A column for '{column_name}' is expected.",
            severity=SeverityLevel.ERROR,
            sheet_name=loaded_sheet.data_sheet_name,
        )

    return result, column


def get_data_loaded_columns(
    data: dict[str, DataSheetMap], rule: str
) -> tuple[list[ValidationResult], dict[str, DataColumnMap]]:
    """Gets a list of data loaded columns if found.

    Args:
        data (dict[str, SheetMap]): column names and data loaded sheet
        rule (str): validation rule

    Returns:
        tuple[List[ValidationResult], dict[str, ColumnMap]]: list of validation errors
             if any, column name and loaded column if found

    """
    results: list[ValidationResult] = []
    loaded_columns: dict[str, DataColumnMap] = {}

    for column, loaded_sheet in data.items():
        result, loaded_column = get_data_loaded_column(loaded_sheet, column, rule)

        if result is None:
            assert loaded_column is not None
            loaded_columns[column] = loaded_column
        else:
            results.append(result)

    return results, loaded_columns


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


def get_data_sheet_id(
    sheet_name: str,
    schema: BaseDatasetSchema,
    loaded_sheet: DataSheetMap,
    rule: str,
    expected: int = 1,
) -> tuple[ValidationResult | None, list[DataColumnMap]]:
    """Gets unique columns for a scheema sheet and loaded sheet.

    Args:
        sheet_name (str): name of sheet
        schema (BaseDatasetSchema): dataset schema
        loaded_sheet (SheetMap):  loaded sheet
        rule (str): validation rule
        expected (int, optional): how many matches are expected. Defaults to 1.

    Returns:
        tuple[ValidationResult | None, List[ColumnMap]]: validation error if any,
             list of column matches if found
    """
    result = None
    ids = get_matching_unique_columns(schema, loaded_sheet, sheet_name)

    if not ids:
        result = ValidationResult(
            rule=rule,
            message=f"A unique id column for '{loaded_sheet.data_sheet_name}' is"
            " expected but none were found.",
            severity=SeverityLevel.ERROR,
            sheet_name=loaded_sheet.data_sheet_name,
        )
    elif len(ids) != expected:
        result = ValidationResult(
            rule=rule,
            message=f"A single unique column for schema sheet '{sheet_name}' and matching"
            f" excel sheet '{loaded_sheet.data_sheet_name}' was expected.",
            severity=SeverityLevel.ERROR,
            sheet_name=sheet_name,
        )
    return result, ids


def get_data_sheet_ids(
    schema: BaseDatasetSchema,
    data: dict[str, DataSheetMap],
    rule: str,
    expected: int = 1,
) -> tuple[list[ValidationResult], dict[str, list[DataColumnMap]]]:
    """Gets unique columns for a list of scheema sheets and loaded sheets.

    Args:
        schema (BaseDatasetSchema): dataset schema
        data (dict[str, SheetMap]): name of sheet, loaded sheet
        rule (str): validation rule
        expected (int, optional): how many matches are expected. Defaults to 1.

    Returns:
        tuple[List[ValidationResult], dict[str, List[ColumnMap]]]: _description_
    """
    results: list[ValidationResult] = []
    loaded_columns: dict[str, list[DataColumnMap]] = {}

    for sheet, loaded_sheet in data.items():
        result, loaded_column = get_data_sheet_id(sheet, schema, loaded_sheet, rule, expected)

        if result is None:
            assert loaded_column is not None
            loaded_columns[sheet] = loaded_column
        else:
            results.append(result)

    return results, loaded_columns


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


def get_matching_id_columns(
    source: list[DataColumnMap],
    source_sheet: str,
    target: list[DataColumnMap],
    target_sheet: str,
    rule: str,
) -> tuple[ValidationResult | None, list[tuple]]:
    """Get matching id columns between sheets.

    Args:
        source (List[ColumnMap]): list of source columns
        source_sheet (str): source sheet
        target (List[ColumnMap]): list of target columns
        target_sheet (str): target sheet
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, list[ColumnMap]]: validation errors if any,
            list of matched columns if found
    """

    result = None

    matching_columns = match_sheet_columns(source, target)
    # should only be one matching id column between the sheets.
    if len(matching_columns) != 1:
        result = ValidationResult(
            rule=rule,
            message=f"Expected 1 linkable ID column for sheets '{source_sheet}' and "
            f" '{target_sheet}' but {len(matching_columns)} were found.",
            severity=SeverityLevel.ERROR,
        )

    if result is None:
        assert matching_columns is not None

    return result, matching_columns


def get_matching_id_columns_alt(
    source: list[DataColumnMap],
    source_sheet: str,
    target: list[DataColumnMap],
    target_sheet: str,
    rule: str,
) -> tuple[ValidationResult | None, list[DataColumnMap], list[DataColumnMap]]:
    """Attempts to find two id like columns that could be used to try
        and link two sheets.

        Only is this if other more direct methods have been tried

    Args:
        source (List[ColumnMap]): list of source columns
        source_sheet (str): source sheet
        target (List[ColumnMap]): list of target columns
        target_sheet (str): target sheet
        rule (str): validation rule

    Returns:
        tuple[ValidationResult | None, list[DataColumnMap], list[DataColumnMap]]:
            validation results, matching id columns from source and target
    """
    result = None

    source_columns, target_columns = match_sheet_columns_ids(source, target)
    if len(source_columns) != 1 or len(target_columns) != 1:
        result = ValidationResult(
            rule=rule,
            message=f"Expected 1 linkable ID column for sheets '{source_sheet}' and"
            f" '{target_sheet}' but '{source_sheet}' had {len(source_columns)} and"
            f" '{target_sheet}' had {len(target_columns)}.",
            severity=SeverityLevel.ERROR,
        )
    if result is None:
        assert source_columns is not None
        assert target_columns is not None

    return result, source_columns, target_columns


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
