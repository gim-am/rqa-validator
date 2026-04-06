from typing import  List


from ..validators.base import ValidationResult, BaseValidator
from ..models.schema import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData



class MandatoryColumns(BaseValidator):
    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:

        results: List[ValidationResult] = []
        for sheet in self.schema.loaded_sheets:
            if not sheet.mandatory_columns:
                continue

            df_columns = data.loaded_sheets[sheet.standard_name]['data'].columns
            for column in sheet.mandatory_columns:
                if not any(map(lambda v: v in df_columns, column.names)):
                    results.append(ValidationResult(
                        message=f'A column for {column.standard_name} was expexted in the {data.loaded_sheets[sheet.standard_name]['original_sheet_name']} sheet but was not found.'
                        ,severity='error'
                        ))


        return results

