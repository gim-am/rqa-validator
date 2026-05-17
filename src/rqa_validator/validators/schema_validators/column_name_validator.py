import re

import polars as pl

from ...loaders.excel_loader import ExcelLoaderData
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult


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
        pattern = re.compile(r"[^a-zA-Z_./\-\\\d:]")
        column_match_df = pl.DataFrame(
            [pl.Series("sheet", [], dtype=pl.String), pl.Series("columns", [], dtype=pl.String)]
        )

        for sheet in data.loaded_sheets:
            matches = list(filter(pattern.search, sheet.data.columns))
            if matches:
                column_match_df = column_match_df.vstack(
                    pl.DataFrame(
                        {"sheet": sheet.data_sheet_name, "columns": match} for match in matches
                    )
                )

        if column_match_df.height > 0:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message="Some sheets had column names"
                    " that appear to be labels instead of variables."
                    " Check the output for details.",
                    severity=SeverityLevel.ERROR,
                    details=column_match_df.to_dict(as_series=False),
                )
            )

        return results
