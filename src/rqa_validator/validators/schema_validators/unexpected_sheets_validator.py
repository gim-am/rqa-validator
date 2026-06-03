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

        if data.unexpected_sheets:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=self._(
                        "unexpected_sheets_validator.unexpected_sheets",
                        count=len(data.unexpected_sheets),
                    ),
                    severity=SeverityLevel.WARNING,
                    details={"unexpected_sheets": data.unexpected_sheets},
                )
            )

        if data.hidden_sheets:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=self._(
                        "unexpected_sheets_validator.hidden_sheets", count=len(data.hidden_sheets)
                    ),
                    severity=SeverityLevel.ERROR,
                    details={"hidden_sheets": data.hidden_sheets},
                )
            )

        return results
