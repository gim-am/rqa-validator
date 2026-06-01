from rqa_validator.common.list_matching import (
    FuzzMatch,
    duplicate_list_items,
    lower_list_items,
    match_list_to_list,
    unique_list,
)
from rqa_validator.config import settings
from rqa_validator.loaders.base import DataColumnMap
from rqa_validator.models.base import SchemaSheetMap
from rqa_validator.validators.base import SeverityLevel, ValidationResult


class BaseExcelLoader:
    def match_excel_columns_to_schema(
        self, excel_columns: list[str], schema_sheet: SchemaSheetMap
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
                            message=f"The schema sheet '{schema_sheet.standard_name}' column"
                            f" '{column.standard_name}' had {len(literal_matches)}"
                            " matches to columns. There should be only 1."
                            "Check the schema.",
                            severity=SeverityLevel.ERROR,
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
                            message=f"The schema sheet '{schema_sheet.standard_name}'"
                            f" column '{column.standard_name}' was fuzzy matched"
                            " with an excel column.  If this was an accurate match consider"
                            " renaming this column in the future. See output for details.",
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
                            message=f"The schema sheet '{schema_sheet.standard_name}'"
                            f" column '{column.standard_name}' was fuzzy matched"
                            " with multiple excel columns so was not matched as"
                            " this would cause validation errors."
                            " See output for details.",
                            severity=SeverityLevel.ERROR,
                            sheet_name=schema_sheet.standard_name,
                            column_name=column.standard_name,
                            details={column.standard_name: fuzzy_matched_values},
                        )
                    )
        return results, matches

    def match_excel_sheet_to_schema(
        self, excel_sheet_name: str, schema_sheets: list[SchemaSheetMap]
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
        fuzzy_matched_values_schema: dict[str, list[FuzzMatch]] = {}

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
                fuzzy_matched_values_schema[sheet_config.standard_name] = fuzzy_matched_values

        if bool(fuzzy_matched_values_schema):
            if len(fuzzy_matched_values_schema.keys()) == 1:
                # fuzzy match to only 1 schema sheet
                sheet_name = list(fuzzy_matched_values_schema.keys())[0]
                results.append(
                    ValidationResult(
                        rule="Match excel sheeet to schema",
                        message=f"Excel sheet '{excel_sheet_name}' was fuzzy matched with"
                        f" schema sheet {sheet_name}. If this was an accurate match consider"
                        f" renaming this excel sheet to {sheet_name} in the future.",
                        severity=SeverityLevel.INFO,
                        sheet_name=excel_sheet_name,
                        details={excel_sheet_name: fuzzy_matched_values_schema},
                    )
                )
                return sheet_name, results
            else:
                # fuzzy match to multiple schema sheets
                results.append(
                    ValidationResult(
                        rule="Match excel sheeet to schema",
                        message=f"Excel sheet '{excel_sheet_name}' was fuzzy matched with"
                        " multiple schema sheets so was not matched. This will lead"
                        " to validation errors about excel sheets not being found."
                        " See output for details.",
                        severity=SeverityLevel.INFO,
                        sheet_name=excel_sheet_name,
                        details={excel_sheet_name: fuzzy_matched_values_schema},
                    )
                )

        return "", results

    def check_duplicate_columns(
        self, columns: list[str], sheet_name: str
    ) -> ValidationResult | None:
        """Checks to see if an excel sheet has duplicate column names once the
        names are lowered.

        Some sheets will have column names like ...iraq and ...Iraq. These are
        technically different so they can be loaded ok but sheets should not have
        columns with the same name.

        Args:
            columns (list[str]): excel sheet columns
            sheet_name (str): name of excel sheet

        Returns:
            ValidationResult | None: validation error if duplicates are found.
        """
        duplicate_columns = duplicate_list_items(lower_list_items(columns))
        if duplicate_columns:
            result = ValidationResult(
                rule="Excel Sheet Loading",
                message=f"Excel sheet '{sheet_name}' has {len(duplicate_columns)} duplicate column"
                " names and could not be loaded. Check the output for details.",
                severity=SeverityLevel.ERROR,
                sheet_name=sheet_name,
                details={"duplicate_columns": unique_list(duplicate_columns)},
            )
            return result
