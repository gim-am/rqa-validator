from dataclasses import dataclass

from ..validators.base import ValidationResult, BaseValidator
from typing import  Any, List

from ..models.base import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData, LoadedSheet
from ..common.matching import filter_list, match_list_to_list

class MissingSheets(BaseValidator):

    @property
    def name(self) -> str:
        return 'MissingSheets'

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

        expected_sheets = [ sheet.standard_name for sheet in  self.schema.schema_loaded_sheets if sheet.required]
        expected_sheets.extend([sheet.standard_name for sheet in  self.schema.schema_unloaded_sheets if sheet.required])

        optional_sheets = [ sheet.standard_name for sheet in  self.schema.schema_loaded_sheets if not sheet.required]
        optional_sheets.extend([sheet.standard_name for sheet in  self.schema.schema_unloaded_sheets if not sheet.required])

        # get keys
        provided_sheets = data.get_loaded_sheet_mapped_names()
        provided_sheets.extend(data.unloaded_sheets)

        missing_sheets = filter_list(expected_sheets, provided_sheets) 
        optional_missing_sheets = filter_list(optional_sheets, provided_sheets)

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

class CrossSheetRowSumCheck(BaseValidator):
    @property
    def name(self) -> str:
        return 'CrossSheetRowSumCheck'
    
    def validate(self, data: ExcelLoaderData, master_sheet: str = 'raw_data'
    , child_sheets: List[str] = ['clean_data', 'deletion_log']) -> List[ValidationResult]:
        """Checks to see if raw_data rows equals clean_data rows plus deletion_log rows.

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

        master_data = data.get_loaded_sheet(master_sheet)
        if master_data:
            master_data_count = master_data.data.height
        else:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {master_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        for sheet in child_sheets:
            child_data = data.get_loaded_sheet(sheet)
            if child_data:
                child_counts.append(ChildCounts(sheet_name=sheet,
                                                row_count=child_data.data.height))
            else:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A sheet for {sheet} was not found. This sheet is required for checking data counts.'
                    ,severity = 'error'
                ))

        if not results:
            child_sum = sum([item.row_count for item in child_counts])
            missing_rows: int = abs(child_sum - master_data_count)
            if missing_rows > 0:
                child_message = ' and '.join([f'{item.sheet_name} ({item.row_count})'for item in child_counts])
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'Summing row counts for sheets {child_message} does not equal {master_sheet} rows ({master_data_count}). The difference is {missing_rows}.'
                    ,severity = 'error'
            ))
                
        return results
            
        
class CrossSheetIdCheck(BaseValidator):
    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema
        
    @property
    def name(self) -> str:
        return 'CrossSheetIdCheck'

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
                message = f'A single unique id column for {master_loaded_sheet.data_sheet_name} is expected but {len(master_matching_columns)} were found. {*master_matching_columns,}'
                ,severity = 'error'
                , sheet_name =  master_loaded_sheet.data_sheet_name
                , column_name = ', '.join(master_matching_columns)
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
                    message = f'A single unique id column for {child_loaded_sheet.data_sheet_name} is expected but {len(child_matching_columns)} were found. {*child_matching_columns,}'
                    ,severity = 'error'
                    , sheet_name = child_loaded_sheet.data_sheet_name
                    , column_name = ', '.join(master_matching_columns)
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
                    message = f'Id values for sheet {child_loaded_sheet.data_sheet_name} and column {child_matching_columns[0]} were not found in sheet {master_loaded_sheet.data_sheet_name} column {master_matching_columns[0]}. ids: {*missing_ids,}'
                    ,severity = 'error'
                    , sheet_name = child_loaded_sheet.data_sheet_name
                    , column_name = ', '.join(master_matching_columns)
                ))
        return results



    
    def _get_matching_columns(self, loaded_data: LoadedSheet, sheet_name: str) -> list[Any] | list[str]:
        """matches schema unique columns to loaded data column

        Args:
            loaded_data (LoadedSheet): the excel loaded data sheet to match with
            sheet_name (str): the schema sheet to match with

        Returns:
            list[Any] | list[str]: a list of matched columns
        """

       
        sheet = self.schema.get_schema_sheet(sheet_name)
        if sheet is not None:
            id_columns = sheet.unique_columns
            
            if id_columns is not None:
                
                 # TODO add fuzzy matching
                return  [column for column in id_columns.combine() if column in loaded_data.columns]
                
        return []


        # check column exists in both raw, clean and deleted
        # get list of sheets with unique ids
        #  see which ids are common across sheets


        # check all idsfrom clean and deleted are in raw












