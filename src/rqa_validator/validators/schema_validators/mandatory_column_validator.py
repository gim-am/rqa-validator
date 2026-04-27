from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, ValidationResult


from typing import List


class MandatoryColumns(BaseValidator):

    @property
    def name(self) -> str:
        return 'MandatoryColumns'

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected mandatory columns are missing
        across relevant sheets. 

        Also checks if unique columns are missing.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []
        for sheet in self.schema.schema_loaded_sheets:

            if not sheet.mandatory_columns:
                continue

            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)
            if loaded_sheet_info is not None:

                for column in sheet.mandatory_columns:
                    if not loaded_sheet_info.get_column_map(column.standard_name):
                        results.append(ValidationResult(
                            rule = self.name,
                            message = f'A column for {column.standard_name} was expexted in the {loaded_sheet_info.data_sheet_name} sheet but was not found.'
                            ,severity = 'error'
                            ,sheet_name = loaded_sheet_info.data_sheet_name
                            ))


            else:
                results.append(ValidationResult(
                                rule = self.name,
                                message = f'No sheet was loaded for {sheet.standard_name}.'
                                ,severity = 'error'
                                ,sheet_name = sheet.standard_name
                                ))


        return results