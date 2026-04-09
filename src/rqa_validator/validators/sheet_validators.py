from ..validators.base import ValidationResult, BaseValidator
from typing import  List

from ..models.schema import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData, LoadedSheet

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
                rule = self.name,
                message = f'A sheet for {sheet} was expexted but was not found.'
                ,severity = 'error'
            ))

        for sheet in optional_missing_sheets:
            if sheet == 'sampling_info':
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A sheet for {sheet} is expected when weights are added to the clean data. Add this sheet if required.'
                    ,severity = 'warning'
                ))
            else:
                results.append(ValidationResult(
                    rule = self.name,
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
                rule = self.name,
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
                rule = self.name,
                message = f'A sheet for {raw_data_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        clean_data = data.get_loaded_sheet(clean_data_sheet)
        if clean_data:
            clean_data_count = clean_data.data.height
        else:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {clean_data_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        deleted_data = data.get_loaded_sheet(deletion_log_sheet)
        if deleted_data:
            deleted_data_count = deleted_data.data.height
        else:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {deletion_log_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        if not results:
            missing_rows = abs(clean_data_count + deleted_data_count - raw_data_count)
            if missing_rows > 0:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'clean_data rows ({clean_data_count}) + deletion_log rows ({deleted_data_count}) does not equal raw_data rows ({raw_data_count}). The difference is {missing_rows}.'
                    ,severity = 'error'
            ))
                
        return results
            
        
class CrossSheetIdCheck(BaseValidator):
    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    name = 'CrossSheetIdCheck'

    def validate(self, data: ExcelLoaderData, 
                    master_sheet: str = 'raw_data',
                    child_sheets: List = ['clean_data', 'deletion_log', 'cleaning_log']) -> List[ValidationResult]:
        """Checks to see if ids from child sheet/s are present in a master/parent sheet

        Args:
            data (ExcelLoaderData): data to be validated
            master_sheet (str, optional): Sheet to make sure that child ids are in. Defaults to 'raw_data'.
            child_sheets (List, optional): Sheet/s to make sure that ids are in master_sheet. Defaults to ['clean_data', 'deletion_log', 'cleaning_log'].

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        master_loaded_sheet = data.get_loaded_sheet(master_sheet)
        
        if not master_loaded_sheet:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {master_sheet} is expected.'
                ,severity = 'error'
            ))  
            return results         
        
        master_matching_columns = self._get_matching_columns(master_loaded_sheet, master_sheet)
        if len(master_matching_columns) != 1:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A single unique id column for {master_loaded_sheet.original_name} is expected but {len(master_matching_columns)} were found. {*master_matching_columns,}'
                ,severity = 'error'
                , sheet_name =  master_loaded_sheet.original_name
                , column_name = master_matching_columns
            ))
            return results

        for sheet in child_sheets:
            child_loaded_sheet  = data.get_loaded_sheet(sheet)
            if not child_loaded_sheet:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A sheet for {sheet} is expected.'
                    ,severity = 'error'
                ))  
                continue

        
            child_matching_columns = self._get_matching_columns(child_loaded_sheet, sheet)    

            if len(child_matching_columns) != 1:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A single unique id column for {child_loaded_sheet.original_name} is expected but {len(child_matching_columns)} were found. {*child_matching_columns,}'
                    ,severity = 'error'
                    , sheet_name=child_loaded_sheet.original_name
                    , column_name=child_matching_columns
                ))
                continue

            # gets ids from a child sheet that are not present in a master sheet
            missing_ids = child_loaded_sheet.data.select(child_matching_columns[0]).join(other=master_loaded_sheet.data.select(master_matching_columns[0]),
                                    how='anti',
                                    left_on=child_matching_columns[0],
                                    right_on=master_matching_columns[0]).to_series().to_list()
            if missing_ids:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'Id values for sheet {child_loaded_sheet.original_name} and column {child_matching_columns[0]} were not found in sheet {master_loaded_sheet.original_name} column {master_matching_columns[0]}. ids: {*missing_ids,}'
                    ,severity = 'error'
                    , sheet_name = child_loaded_sheet.original_name
                    , column_name = child_matching_columns[0]
                ))
        return results



    
    def _get_matching_columns(self, loaded_data: LoadedSheet, sheet_name: str):
        id_columns = self.schema.get_loaded_sheet(sheet_name).unique_columns.combine()
        if not id_columns:
            return []
        else:
            return  [column for column in id_columns if column in loaded_data.columns]


        # check column exists in both raw, clean and deleted
        # get list of sheets with unique ids
        #  see which ids are common across sheets


        # check all idsfrom clean and deleted are in raw












