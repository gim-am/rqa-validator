import polars as pl

from rqa_validator.config import settings

from ...common.list_matching import filter_list, match_list_to_list
from ...loaders.base import DataColumnMap
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult
from ..data_helpers import get_data_sheet_id
from ..options import PII_PATTERN_EXPRESSIONS, PII_PATTERNS, get_pii_columns


class PiiDataCheck(BaseValidator):
    """Checks all the sheets for possible PII Data"""

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    @property
    def name(self) -> str:
        return "PiiDataCheck"

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """This performs two sets of checks

        First: checks to see if any pii columns are present across relevant sheets.
            Possible pii columns are currently stored in models/config.
            Fuzzy matching is also optionally performed.

        Second: performs regex matching on sheets for possible pii data.
            Currently matching is fairly simple and limited to:
            - emails
            - possible phone numbers: must start with a 0 or +
                and not be a decimal. This is a limited implementaion.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: list[ValidationResult] = []
        pii_columns = get_pii_columns()

        match_records = []

        for sheet in data.loaded_sheets:
            filtered_df = sheet.data.select(
                filter_list(sheet.data.columns, settings.IGNORE_COLUMNS_FOR_VALIDATION)
            )
            # scan column names
            literal_matches, fuzzy_matched_values = match_list_to_list(
                filtered_df.columns, pii_columns, settings.FUZZY_MATCH_COLUMNS
            )

            if literal_matches:
                match_records.extend(
                    [
                        {
                            "sheet": sheet.data_sheet_name,
                            "column": item,
                            "match_type": "literal",
                            "match_values": item,
                        }
                        for item in literal_matches
                    ]
                )

            if fuzzy_matched_values:
                match_records.extend(
                    [
                        {
                            "sheet": sheet.data_sheet_name,
                            "column": item.standard_name,
                            "match_type": "fuzzy",
                            "match_values": str(item.matches),
                        }
                        for item in fuzzy_matched_values
                    ]
                )

            # scan column data
            result, id_column = get_data_sheet_id(
                sheet.data_sheet_name, self.schema, sheet, self.name
            )

            if not id_column:
                id_column = DataColumnMap(
                    data_column_name="row_index", schema_column_name="row_index"
                )
                melted_df = filtered_df.with_row_index(id_column.data_column_name).unpivot(
                    index=id_column.data_column_name,
                    variable_name="column_name",
                    value_name="value",
                )
            else:
                id_column = id_column[0]
                # unpivot to make showing the results easier
                melted_df = filtered_df.unpivot(
                    index=id_column.data_column_name,
                    variable_name="column_name",
                    value_name="value",
                )

            # add expression columns
            melted_df = melted_df.with_columns(PII_PATTERN_EXPRESSIONS)
            # build match conditions
            match_conditions = [pl.col(name=f"match_{t}").is_not_null() for t in PII_PATTERNS]

            # apply conditions and filter the data
            any_match_condition = pl.any_horizontal(match_conditions)
            filtered_df = melted_df.filter(any_match_condition)

            match_cols = [f"match_{t}" for t in PII_PATTERNS]

            # format results for output
            final_df = filtered_df.unpivot(
                index=[id_column.data_column_name, "column_name"],
                on=match_cols,
                variable_name="pii_type_raw",
                value_name="matched_value",
            )
            # unpivot will add extra rows so remove those that havent actually matched
            final_df = final_df.filter(pl.col("matched_value").is_not_null())

            final_df = final_df.with_columns(
                pl.col("pii_type_raw").str.replace("match_", "").alias("pii_type")
            ).select([id_column.data_column_name, "column_name", "pii_type", "matched_value"])

            if final_df.height > 0:
                results.append(
                    ValidationResult(
                        rule=self.name,
                        message=f"The sheet '{sheet.data_sheet_name}' contains possible"
                        " pii data. Check the output for details.",
                        severity=SeverityLevel.ERROR,
                        sheet_name=sheet.data_sheet_name,
                        details=final_df.to_dict(),
                    )
                )
        if match_records:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message="Possible Pii columns were found. Check the output for details.",
                    severity=SeverityLevel.WARNING,
                    details=pl.DataFrame(match_records).to_dict(as_series=False),
                )
            )

        return results
