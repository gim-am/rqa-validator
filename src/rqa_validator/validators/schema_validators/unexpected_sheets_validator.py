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
                    message=f"{len(data.unexpected_sheets)} unexpected sheets were found in the"
                    " dataset. Check to see if these are required to be published/archived."
                    " Check output for details.",
                    severity=SeverityLevel.WARNING,
                    details={"unexpected_sheets": data.unexpected_sheets},
                )
            )

        if data.hidden_sheets:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"There are {len(data.hidden_sheets)} hidden sheets in the dataset."
                    " Check to see if these should be shown or removed before the dataset is"
                    " published/archived. Check output for details.",
                    severity=SeverityLevel.ERROR,
                    details={"hidden_sheets": data.hidden_sheets},
                )
            )

        return results
