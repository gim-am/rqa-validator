from ...common.list_matching import filter_list
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult


class MissingSheetsCheck(BaseValidator):
    @property
    def name(self) -> str:
        return "MissingSheetsCheck"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """Checks to see if any expected sheets are missing
        across a dataset.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: list[ValidationResult] = []

        expected_sheets = [
            sheet.standard_name
            for sheet in self.schema.schema_loaded_sheets
            if sheet.required
        ]
        expected_sheets.extend(
            [
                sheet.standard_name
                for sheet in self.schema.schema_unloaded_sheets
                if sheet.required
            ]
        )

        optional_sheets = [
            sheet.standard_name
            for sheet in self.schema.schema_loaded_sheets
            if not sheet.required
        ]
        optional_sheets.extend(
            [
                sheet.standard_name
                for sheet in self.schema.schema_unloaded_sheets
                if not sheet.required
            ]
        )

        # get keys
        provided_sheets = data.get_loaded_sheet_mapped_names()
        provided_sheets.extend(data.get_unloaded_sheet_mapped_names())

        missing_sheets = filter_list(expected_sheets, provided_sheets)
        optional_missing_sheets = filter_list(optional_sheets, provided_sheets)

        for sheet in missing_sheets:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"A sheet for {sheet} was expexted but was not found.",
                    sheet_name=sheet,
                    severity=SeverityLevel.ERROR,
                )
            )

        for sheet in optional_missing_sheets:
            if sheet == "sampling_info":
                results.append(
                    ValidationResult(
                        rule=self.name,
                        message=f"A sheet for {sheet} is expected when weights are\
                              added to the clean data. Add this sheet if required.",
                        sheet_name=sheet,
                        severity=SeverityLevel.WARNING,
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        rule=self.name,
                        message=f"A sheet for {sheet} is optional. Check if this sheet\
                              is required or not for this dataset.",
                        sheet_name=sheet,
                        severity=SeverityLevel.WARNING,
                    )
                )

        return results
