from rqa_validator.loaders.excel_loader import ExcelLoaderData
from rqa_validator.validators.base import BaseValidator, ValidationResult


from typing import List


class UnexpectedSheets(BaseValidator):
    @property
    def name(self) -> str:
        return 'UnexpectedSheets'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if there are any unexpected sheets 
        across a dataset. 

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """

        results: List[ValidationResult] = []

        for sheet in data.unexpected_sheets:
            results.append(ValidationResult(
                rule = self.name,
                message = f'An unexpected sheet {sheet} was found. Check if this is required to be published/archived.'
                ,severity = 'warning'
            ))

        return results