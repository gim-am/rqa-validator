from ...loaders.excel_loader import ExcelLoaderData
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult


class UnexpectedSheetsCheck(BaseValidator):
    @property
    def name(self) -> str:
        return "UnexpectedSheetsCheck"

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """Checks to see if there are any unexpected sheets
        across a dataset.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """

        results: list[ValidationResult] = []

        for sheet in data.unexpected_sheets:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"An unexpected sheet '{sheet}' was found. Check if this is"\
                          " required to be published/archived.",
                    severity=SeverityLevel.WARNING,
                )
            )

        return results
