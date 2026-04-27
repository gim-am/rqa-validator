from rqa_validator.loaders.excel_loader import ExcelLoaderData
from rqa_validator.validators.base import BaseValidator, ValidationResult


import re
from typing import List


class ColumnNameCheck(BaseValidator):
    """Check column names are variables instead of labels. 

    """
    @property
    def name(self) -> str:
        return 'ColumnNameCheck'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Check column names are variables instead of labels.

        This is done through regex matching that checks if there
        are any characters other than:
        - A-Z
        - a-z
        - 0-9
        - . or _

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: list of validation errors
        """
        results: List[ValidationResult] = []
        pattern = re.compile(r'[^a-zA-Z_.\d:]')

        for sheet in data.loaded_sheets:
            matches = list(filter(pattern.search, sheet.data_columns))
            if matches:

                results.append(ValidationResult(
                    rule = self.name ,
                    message = f'The sheet {sheet.data_sheet_name} has column names that appear to be labels instead of variables. Check the output for details.'
                    ,severity = 'error'
                    ,sheet_name = sheet.data_sheet_name
                    , details= {sheet.data_sheet_name: matches}
                    ))

        return results