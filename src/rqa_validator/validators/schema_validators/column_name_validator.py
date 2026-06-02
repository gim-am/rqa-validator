import polars as pl

from ...loaders.excel_loader import ExcelLoaderData
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult
from ...validators.options import COLUMN_NAME_VALIDATOR_PATTERN


class ColumnNameCheck(BaseValidator):
    """Check column names are variables instead of labels."""

    @property
    def name(self) -> str:
        return "ColumnNameCheck"

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """Check column names are variables instead of labels.

        This is done through regex matching that checks if there
        are any characters other than:
        - A-Z
        - a-z
        - 0-9
        - . or _ or - or / or \\

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: list of validation errors
        """
        results: list[ValidationResult] = []

        match_records = []

        for sheet in data.loaded_sheets:
            matches = list(filter(COLUMN_NAME_VALIDATOR_PATTERN.search, sheet.data.columns))
            if matches:
                match_records.extend(
                    [
                        {
                            "sheet": sheet.data_sheet_name,
                            "columns": item,
                        }
                        for item in matches
                    ]
                )

        if match_records:
            column_match_df = pl.DataFrame(match_records)
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"{column_match_df.select(pl.col('sheet')).unique().height} sheets had"
                    " column names that appear to be labels instead of variables."
                    " Check the output for details.",
                    severity=SeverityLevel.ERROR,
                    details=column_match_df.to_dict(as_series=False),
                )
            )

        return results
