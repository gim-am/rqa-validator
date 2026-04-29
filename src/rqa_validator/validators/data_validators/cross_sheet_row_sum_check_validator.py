from ...validators.helpers import get_data_loaded_sheets

from ...loaders.excel_loader import ExcelLoaderData
from ...validators.base import BaseValidator, ValidationResult


from dataclasses import dataclass
from typing import List


class CrossSheetRowSumCheck(BaseValidator):

    def __init__(self, master_sheet: str = 'raw_data'
                 , child_sheets: List[str] = ['clean_data', 'deletion_log']):
        """
        Checks to see if master_sheet rows equals the sum of child sheet rows 

        Args:
            master_sheet (str, optional): Sheet to make sure that child ids are in. Defaults to 'raw_data'.
            child_sheets (List, optional): Sheet/s to make sure that ids are in master_sheet. Defaults to ['clean_data', 'deletion_log', 'cleaning_log'].
        """
        self.master_sheet = master_sheet
        self.child_sheets = child_sheets
    @property
    def name(self) -> str:
        return 'CrossSheetRowSumCheck'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if master_sheet rows equals the sum of child sheet rows rows.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []
        master_data_count:int = 0

        @dataclass
        class ChildCounts():
            sheet_name: str
            row_count:int

        child_counts: List[ChildCounts] = []

        result, data_loaded_sheets = get_data_loaded_sheets(data=data, 
                                                       sheet_names=[self.master_sheet, 
                                                                    *self.child_sheets],
                                                        rule=self.name)

        if result:
            results.extend(result)
            return results
       
        master_data_count = data_loaded_sheets[self.master_sheet].data.height

        for sheet in self.child_sheets:  
            child_counts.append(ChildCounts(sheet_name=sheet,
                                            row_count=data_loaded_sheets[sheet].data.height))
       
        child_sum = sum([item.row_count for item in child_counts])
        missing_rows: int = abs(child_sum - master_data_count)
        if missing_rows > 0:
            child_message = ' and '.join([f'{item.sheet_name} ({item.row_count})'for item in child_counts])
            results.append(ValidationResult(
                rule = self.name,
                message = f'Sum of row counts for sheets {child_message} does not equal {self.master_sheet} rows ({master_data_count}). The difference is {missing_rows}.'
                ,severity = 'error'
        ))

        return results