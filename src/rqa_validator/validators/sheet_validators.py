from ..validators.base import ValidationResult, BaseValidator
from typing import  List

from ..models.schema import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData

class MissingSheets(BaseValidator):
    name = "MissingSheets"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected sheets are missing
        across a dataset. 

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        expected_sheets = [ sheet.standard_name for sheet in  self.schema.loaded_sheets if sheet.required]
        expected_sheets.extend([sheet.standard_name for sheet in  self.schema.unloaded_sheets if sheet.required])

        optional_sheets = [ sheet.standard_name for sheet in  self.schema.loaded_sheets if not sheet.required]
        optional_sheets.extend([sheet.standard_name for sheet in  self.schema.unloaded_sheets if not sheet.required])

        # get keys
        provided_sheets = data.get_loaded_sheet_mapped_names()
        provided_sheets.extend(data.unloaded_sheets)

        missing_sheets = [sheet for sheet in expected_sheets if sheet not in provided_sheets]
        optional_missing_sheets = [sheet for sheet in optional_sheets if sheet not in provided_sheets]

        for sheet in missing_sheets:
            results.append(ValidationResult(
                message=f'A sheet for {sheet} was expexted but was not found.'
                ,severity='error'
            ))

        for sheet in optional_missing_sheets:
            if sheet == 'sampling_info':
                results.append(ValidationResult(
                    message=f'A sheet for {sheet} is expected when weights are added to the clean data. Add this sheet if required.'
                    ,severity='warning'
                ))
            else:
                results.append(ValidationResult(
                    message=f'A sheet for {sheet} is optional. Check if this sheet is required or not for this dataset.'
                    ,severity='warning'
                ))

        return results
    
class UnexpectedSheets(BaseValidator):
    name = "UnexpectedSheets"
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
                message=f'An unexpected sheet {sheet} was found. Check if this is required to be published/archived.'
                ,severity='warning'
            ))

        return results

            


