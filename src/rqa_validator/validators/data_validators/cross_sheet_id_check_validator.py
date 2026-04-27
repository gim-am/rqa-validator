from rqa_validator.common.list_matching import match_sheet_columns
from rqa_validator.common.schema_matching import get_matching_unique_columns
from rqa_validator.loaders.excel_loader import ExcelLoaderData
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator, ValidationResult


from typing import List


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