from ...validators.helpers import get_data_loaded_sheet, get_data_loaded_sheets, get_data_sheet_ids, get_matching_id_columns

from ...common.schema_matching import get_matching_unique_columns
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, ValidationResult


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

        result, data_loaded_sheets = get_data_loaded_sheets(data=data, 
                                                       sheet_names=[self.master_sheet],
                                                        rule=self.name)

        if result:
            results.extend(result)
            return results

        result, data_sheet_ids = get_data_sheet_ids(schema=self.schema, 
                                                       data = {self.master_sheet: data_loaded_sheets[self.master_sheet]},
                                                        rule=self.name)
        
        if result:
            results.extend(result)
            return results 
       
        master_matching_columns = data_sheet_ids[self.master_sheet][0]

        for sheet in self.child_sheets:
            result, child_loaded_sheet = get_data_loaded_sheet(data, sheet, self.name)

            if result is not None:
                results.append(result)
                continue
            assert child_loaded_sheet is not None

            # gets ids from a child sheet that are not present in a master sheet

            # this process assumes that:
            # if both sheets have a unique column then these should be compared
            # if one sheet does not have a unique id column then a match is attempted
            #   based on schema name.

            child_matching_columns = get_matching_unique_columns(self.schema, child_loaded_sheet, sheet)

            if not child_matching_columns:
                # some sheets will have a non unique uuid column so try to match based on name
                
                result, matching_columns = get_matching_id_columns(child_loaded_sheet.column_map, child_loaded_sheet.data_sheet_name, [master_matching_columns], self.master_sheet, self.name)
                if result is not None:
                    results.append(result)
                    continue
                assert matching_columns is not None                

            child_matching_columns = child_matching_columns[0]

            missing_ids = child_loaded_sheet.data.select(child_matching_columns.data_column_name).join(
                                    other=data_loaded_sheets[self.master_sheet].data.select(master_matching_columns.data_column_name),
                                    how='anti',
                                    left_on=child_matching_columns.data_column_name,
                                    right_on=master_matching_columns.data_column_name).to_series().to_list()
            if missing_ids:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'Id values for sheet {child_loaded_sheet.data_sheet_name} and column {child_matching_columns.data_column_name} were not found in sheet {data_loaded_sheets[self.master_sheet].data_sheet_name} column {master_matching_columns.data_column_name}. Check output for details. '
                    ,severity = 'error'
                    , sheet_name = child_loaded_sheet.data_sheet_name
                    , column_name = child_matching_columns.data_column_name
                    , details=  {child_matching_columns.data_column_name: missing_ids}
                ))

        return results