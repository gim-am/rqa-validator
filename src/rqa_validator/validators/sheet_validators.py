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
                message = f'A sheet for {sheet} was expexted but was not found.'
                ,severity = 'error'
            ))

        for sheet in optional_missing_sheets:
            if sheet == 'sampling_info':
                results.append(ValidationResult(
                    message = f'A sheet for {sheet} is expected when weights are added to the clean data. Add this sheet if required.'
                    ,severity = 'warning'
                ))
            else:
                results.append(ValidationResult(
                    message = f'A sheet for {sheet} is optional. Check if this sheet is required or not for this dataset.'
                    ,severity = 'warning'
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
                message = f'An unexpected sheet {sheet} was found. Check if this is required to be published/archived.'
                ,severity = 'warning'
            ))

        return results

class DataSumCheck(BaseValidator):
    name = "DataSumCheck"
    def validate(self, data: ExcelLoaderData, raw_data_sheet: str = 'raw_data'
    , clean_data_sheet: str = 'clean_data', deletion_log_sheet: str = 'deletion_log') -> List[ValidationResult]:
        """Checks to see if raw_data rows equals clean_data rows plus deletion_log rows.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        raw_data = data.get_loaded_sheet(raw_data_sheet)
        if raw_data:
            raw_data_count = raw_data.data.height
        else:
            results.append(ValidationResult(
                message = f'A sheet for {raw_data_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        clean_data = data.get_loaded_sheet(clean_data_sheet)
        if clean_data:
            clean_data_count = clean_data.data.height
        else:
            results.append(ValidationResult(
                message = f'A sheet for {clean_data_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        deleted_data = data.get_loaded_sheet(deletion_log_sheet)
        if deleted_data:
            deleted_data_count = deleted_data.data.height
        else:
            results.append(ValidationResult(
                message = f'A sheet for {deletion_log_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        if not results:
            missing_rows = abs(clean_data_count + deleted_data_count - raw_data_count)
            if missing_rows > 0:
                results.append(ValidationResult(
                message = f'clean_data rows ({clean_data_count}) + deletion_log rows ({deleted_data_count}) does not equal raw_data rows ({raw_data_count}). The difference is {missing_rows}.'
                ,severity = 'error'
            ))
                
        return results
            
        











