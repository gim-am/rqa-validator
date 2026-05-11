from config import settings

from ..common.list_matching import FuzzMatch, match_list_to_list
from ..models.base import SchemaSheetMap
from ..validators.base import SeverityLevel, ValidationResult
from .base import DataColumnMap


def match_excel_columns_to_schema(
    excel_columns: list, schema_sheet: SchemaSheetMap
) -> tuple[list[ValidationResult], list[DataColumnMap]]:
    """trys to match an excel column to a schema column.

        First, a literal match is attempted. If one is found this
        is returned

        If there is no literal match and fuzzy matching is enabled
        then a fuzzy match is attempted. If a match is made to only
        one column then this is returned. If a match is made to more than
        one column then no match is returned.

    Args:
        excel_columns (List): list of escel columns
        schema_sheet (SchemaSheetMap): schema sheet to search against

    Returns:
        tuple[List[ValidationResult], List[DataColumnMap]]: _description_
    """
    results: list[ValidationResult] = []
    matches: list[DataColumnMap] = []

    for column in schema_sheet.mandatory_columns:
        literal_matches, fuzzy_matched_values = match_list_to_list(
            column.combine(), excel_columns, fuzzy_match=settings.FUZZY_MATCH_SHEETS
        )

        if literal_matches:
            if len(literal_matches) == 1:
                # because the schema is prevalidated there should only
                # be one literal match unless there are multiple alternate
                # name matches
                matches.append(
                    DataColumnMap(
                        data_column_name=literal_matches[0],
                        schema_column_name=column.standard_name,
                    )
                )

            else:
                # ideally this should not happen
                results.append(
                    ValidationResult(
                        rule="Match excel column to schema",
                        message=f"The schema sheet {schema_sheet.standard_name} column\
                              {column.standard_name} had {len(literal_matches)} matches\
                                  to columns. There should be only 1. Check the schema."
                        ,severity=SeverityLevel.ERROR,
                        sheet_name=schema_sheet.standard_name,
                        column_name=column.standard_name,
                        details={"Literal Match Columns": literal_matches},
                    )
                )
            continue
        elif fuzzy_matched_values:
            if len(fuzzy_matched_values[0].matches) == 1:
                matches.append(
                    DataColumnMap(
                        data_column_name=list(fuzzy_matched_values[0].matches)[0],
                        schema_column_name=column.standard_name,
                    )
                )

                results.append(
                    ValidationResult(
                        rule="Match excel column to schema",
                        message=f"The schema sheet {schema_sheet.standard_name}\
                                column {column.standard_name} was fuzzy matched with\
                                an excel column. See output for details.",
                        severity=SeverityLevel.INFO,
                        sheet_name=schema_sheet.standard_name,
                        column_name=column.standard_name,
                        details={column.standard_name: fuzzy_matched_values},
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        rule="Match excel column to schema",
                        message=f"The schema sheet {schema_sheet.standard_name}\
                                column {column.standard_name} was fuzzy matched\
                                with multiple excel columns so was not matched as\
                                this would cause validation errors.\
                                See output for details.",
                        severity=SeverityLevel.ERROR,
                        sheet_name=schema_sheet.standard_name,
                        column_name=column.standard_name,
                        details={column.standard_name: fuzzy_matched_values},
                    )
                )
    return results, matches


def match_excel_sheet_to_schema(
    excel_sheet_name: str, schema_sheets: list[SchemaSheetMap]
) -> tuple[str, list[ValidationResult]]:
    """Trys to match an excel sheet name to a schema sheet name.

        First, a literal match is attempted. If one is found this
        is returned

        If there is no literal match and fuzzy matching is enabled
        then a fuzzy match is attempted. If a match is made to only
        one sheet then this is returned. If a match is made to more than
        one sheet then no match is returned.
    Args:
        sheet_name (str): excel sheet to be matched
        schema_sheets (List[SheetMapping]): schema sheets to match to.

    Returns:
        tuple[str, List[ValidationResult]]: the schema sheet standard name
        if matched, a list of any validation warnings if relevant.
    """
    results: list[ValidationResult] = []
    fuzzy_matched_values_schema: list[FuzzMatch] = []

    for sheet_config in schema_sheets:
        literal_matches, fuzzy_matched_values = match_list_to_list(
            sheet_config.combine_sheet_names(),
            [excel_sheet_name],
            fuzzy_match=settings.FUZZY_MATCH_SHEETS,
        )

        if literal_matches:
            # clear warning as they are not relevant if a literal match is found
            results = []
            return sheet_config.standard_name, results
        elif fuzzy_matched_values:
            fuzzy_matched_values_schema.extend(fuzzy_matched_values)

    if fuzzy_matched_values_schema:
        if len(fuzzy_matched_values_schema) == 1:
            # fuzzy match to only 1 schema sheet
            results.append(
                ValidationResult(
                    rule="Match excel sheeet to schema",
                    message=f"Excel sheet {excel_sheet_name} was fuzzy matched with\
                          schema sheet {fuzzy_matched_values_schema[0].standard_name}.",
                    severity=SeverityLevel.INFO,
                    sheet_name=excel_sheet_name,
                    details={excel_sheet_name: fuzzy_matched_values_schema},
                )
            )
            return fuzzy_matched_values_schema[0].standard_name, results
        else:
            # fuzzy match to multiple schema sheets
            results.append(
                ValidationResult(
                    rule="Match excel sheeet to schema",
                    message=f"Excel sheet {excel_sheet_name} was fuzzy matched with\
                            multiple schema sheets so was not matched. This will lead\
                            to validation errors about excel sheets not being found.\
                            See output for details.",
                    severity=SeverityLevel.INFO,
                    sheet_name=excel_sheet_name,
                    details={excel_sheet_name: fuzzy_matched_values_schema},
                )
            )

    return "", results
