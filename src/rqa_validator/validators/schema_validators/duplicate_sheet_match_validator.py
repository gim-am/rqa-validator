from ...common.list_matching import duplicate_list_items
from ...loaders.excel_loader import ExcelLoaderData
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult


class DuplicateSheetMatches(BaseValidator):
    @property
    def name(self) -> str:
        return "DuplicateSheetMatches"

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """Checks to see if a schema sheet was matched to multiple excel sheets.

        Args:
            data (ExcelLoaderData): excel data

        Returns:
            List[ValidationResult]: list of validation errors.
        """
        results: list[ValidationResult] = []

        provided_sheets = data.get_loaded_sheet_mapped_names()
        provided_sheets.extend(data.get_unloaded_sheet_mapped_names())
        # duplicates should be a unique list
        duplicates = duplicate_list_items(provided_sheets)

        if duplicates:
            for item in duplicates:
                matched_sheets = data.get_sheet_matches(item)
                sheet_names = [name.data_sheet_name for name in matched_sheets]
                results.append(
                    ValidationResult(
                        rule=self.name,
                        message=f"Multiple excel sheets, {sheet_names}, were mapped\
                                to the same schema sheet {item}. There should be at\
                                 most a 1-1 mapping for each sheet.",
                        severity=SeverityLevel.ERROR,
                        sheet_name=item,
                    )
                )

        return results
