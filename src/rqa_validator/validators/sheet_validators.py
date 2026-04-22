from dataclasses import dataclass

from ..validators.base import ValidationResult, BaseValidator
from typing import  List

from ..models.base_dataset import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData
from ..common.list_matching import duplicate_list_items, filter_list, match_sheet_columns
from ..common.schema_matching import get_matching_unique_columns


class DuplicateSheetMatches(BaseValidator):
    @property
    def name(self) -> str:
        return 'DuplicateSheetMatches'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if a schema sheet was matched to multiple excel sheets. 

        Args:
            data (ExcelLoaderData): excel data

        Returns:
            List[ValidationResult]: list of validation errors.
        """
        results: List[ValidationResult] = []
        
        provided_sheets = data.get_loaded_sheet_mapped_names()
        provided_sheets.extend(data.get_unloaded_sheet_mapped_names())
        # duplicates should be a unique list
        duplicates = duplicate_list_items(provided_sheets)

        if duplicates:
            for item in duplicates:
                matched_sheets = data.get_sheet_matches(item)
                sheet_names = [name.data_sheet_name for name in matched_sheets]
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'Multiple excel sheets, {sheet_names}, were mapped to the same schema sheet {item}. There should be at most a 1-1 mapping for each sheet.'
                    ,severity = 'error'
                    ,sheet_name=item
                ))

        return results


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
        provided_sheets.extend(data.get_unloaded_sheet_mapped_names())

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

        master_data = data.get_loaded_sheet(self.master_sheet)
        if master_data:
            master_data_count = master_data.data.height
        else:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {self.master_sheet} was not found. This sheet is required for checking data counts.'
                ,severity = 'error'
            ))

        for sheet in self.child_sheets:
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
                    message = f'Sum of row counts for sheets {child_message} does not equal {self.master_sheet} rows ({master_data_count}). The difference is {missing_rows}.'
                    ,severity = 'error'
            ))
                
        return results
            
        
class CrossSheetIdCheck(BaseValidator):
    def __init__(self, schema: BaseDatasetSchema, 
                 master_sheet: str = 'raw_data'
                 ,child_sheets: List[str] = ['clean_data', 'deletion_log', 'cleaning_log']):
        """Checks to see if ids from child sheet/s are present in a master/parent sheet

        Args:
            schema (BaseDatasetSchema): dataset schema
           master_sheet (str, optional): Sheet to make sure that child ids are in. Defaults to 'raw_data'.
            child_sheets (List, optional): Sheet/s to make sure that ids are in master_sheet. Defaults to ['clean_data', 'deletion_log', 'cleaning_log'].
        """
        self.master_sheet = master_sheet
        self.child_sheets = child_sheets
        self.schema = schema
        
    @property
    def name(self) -> str:
        return 'CrossSheetIdCheck'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if ids from child sheet/s are present in a master/parent sheet

            this process assumes that:
                -if both sheets have a unique column then these should be compared
                -if one sheet does not have a unique id column then a match is attempted
                based on schema name.
        Args:
            data (ExcelLoaderData): data to be validated
           
        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        master_loaded_sheet = data.get_loaded_sheet(self.master_sheet)
        
        if not master_loaded_sheet:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A sheet for {self.master_sheet} is expected.'
                ,severity = 'error'
            ))  
            return results     
            
        # likely only 1 column
        master_matching_columns = get_matching_unique_columns(self.schema,master_loaded_sheet, self.master_sheet)
        if not master_matching_columns or len(master_matching_columns) > 1:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A single unique id column for {master_loaded_sheet.data_sheet_name} is expected but none were found.'
                ,severity = 'error'
                , sheet_name =  master_loaded_sheet.data_sheet_name
                # , column_name = ', '.join(master_matching_columns)
            ))
            return results
        master_matching_columns = master_matching_columns[0]

        for sheet in self.child_sheets:
            child_loaded_sheet  = data.get_loaded_sheet(sheet)
            if not child_loaded_sheet:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A sheet for {sheet} is expected.'
                    ,severity = 'error'
                ))  
                continue

            # gets ids from a child sheet that are not present in a master sheet
            
            # this process assumes that:
            # if both sheets have a unique column then these should be compared
            # if one sheet does not have a unique id column then a match is attempted
            #   based on schema name.
            
            child_matching_columns = get_matching_unique_columns(self.schema, child_loaded_sheet, sheet)  

            if not child_matching_columns:
                # some sheets will have a non unique uuid column so try to match based on name
                child_matching_columns = match_sheet_columns(child_loaded_sheet.column_map, 
                                                             [master_matching_columns])
            if len(child_matching_columns) != 1:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A unique or matching id column for {child_loaded_sheet.data_sheet_name} is expected but none were found. '
                    ,severity = 'error'
                    , sheet_name = child_loaded_sheet.data_sheet_name
                ))
                continue

            child_matching_columns = child_matching_columns[0]        
            
            missing_ids = child_loaded_sheet.data.select(child_matching_columns.data_column_name).join(
                                    other=master_loaded_sheet.data.select(master_matching_columns.data_column_name),
                                    how='anti',
                                    left_on=child_matching_columns.data_column_name,
                                    right_on=master_matching_columns.data_column_name).to_series().to_list()
            if missing_ids:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'Id values for sheet {child_loaded_sheet.data_sheet_name} and column {child_matching_columns.data_column_name} were not found in sheet {master_loaded_sheet.data_sheet_name} column {master_matching_columns.data_column_name}. Check output for details. '
                    ,severity = 'error'
                    , sheet_name = child_loaded_sheet.data_sheet_name
                    , column_name = child_matching_columns.data_column_name
                    , details=  {child_matching_columns.data_column_name: missing_ids}
                ))

        return results


















