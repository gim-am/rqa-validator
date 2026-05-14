import polars as pl

from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult
from ..data_helpers import get_data_loaded_columns, get_data_loaded_sheets


class MandatoryColumns(BaseValidator):
    @property
    def name(self) -> str:
        return "MandatoryColumns"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """Checks to see if any expected mandatory columns are missing
        across relevant sheets.

        Also checks if unique columns are missing.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: list[ValidationResult] = []

        result, data_loaded_sheets = get_data_loaded_sheets(
            data=data,
            sheet_names=self.schema.get_loaded_sheets_standard_names(),
            rule=self.name,
        )

        if result:
            sheet_df = pl.DataFrame(
                [
                    {
                        "sheet": item.sheet_name,
                    }
                    for item in result
                ]
            ).to_dict(as_series=False)
            results.append(
                ValidationResult(
                    rule=self.name,
                    message="Some excel sheets were expected but not found."
                    " See output for details.",
                    severity=SeverityLevel.ERROR,
                    details=sheet_df,
                )
            )

            return results

        for sheet, loaded_sheet in data_loaded_sheets.items():
            # get all the columns expected for the sheet
            search_columns = self.schema.get_sheet_column_standard_names(sheet)
            # sheet it checked above
            assert search_columns is not None

            search_items = {key: loaded_sheet for key in search_columns}

            # try to get all the loaded columns
            result, columns = get_data_loaded_columns(search_items, self.name)

            if result:
                results.extend(result)

        if results:
            column_df = pl.DataFrame(
                [{"sheet": item.sheet_name, "column": item.column_name} for item in results]
            ).to_dict(as_series=False)
            result = ValidationResult(
                rule=self.name,
                message="Some excel columns were expected but not found. See output for details.",
                severity=SeverityLevel.ERROR,
                details=column_df,
            )
            return [result]

        return results
