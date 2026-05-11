from dataclasses import dataclass

from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult
from ...validators.helpers import get_data_loaded_sheets, get_data_sheet_id


class CrossSheetRowSumCheck(BaseValidator):
    def __init__(
        self,
        schema: BaseDatasetSchema,
        master_sheet: str = "raw_data",
        child_sheets: list[str] = ["clean_data", "deletion_log"],
        master_deletion_log: str | None = None,
    ):
        """
        Checks to see if master_sheet rows equals the sum of child sheet rows

        Args:
            master_sheet (str, optional): Sheet to make sure that child ids are in.
                Defaults to 'raw_data'.
            child_sheets (List, optional): Sheet/s to make sure that ids are in
                master_sheet. Dont pass deletion log here if processing loops.
                Defaults to ['clean_data', 'deletion_log'].
            master_deletion_log (str, optional): if loops are being processed,
                specify the deletion log here to make sure the correct deletion count
                 is used. Dont pass it as a child sheet in this case.
        """
        self.schema = schema
        self.master_sheet = master_sheet
        self.child_sheets = child_sheets
        self.master_deletion_log = master_deletion_log

    @property
    def name(self) -> str:
        return "CrossSheetRowSumCheck"

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """Checks to see if master_sheet rows equals the sum of child sheet rows rows.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: list[ValidationResult] = []
        master_data_count: int = 0
        deleted_data_count: int | None = None

        @dataclass
        class ChildCounts:
            sheet_name: str
            row_count: int

        child_counts: list[ChildCounts] = []

        sheets_to_load = [self.master_sheet, *self.child_sheets]
        if self.master_deletion_log is not None:
            sheets_to_load.append(self.master_deletion_log)

        result, data_loaded_sheets = get_data_loaded_sheets(
            data=data, sheet_names=sheets_to_load, rule=self.name
        )
        if result:
            results.extend(result)
            return results

        # if this is a child sheet then just using the deletion log count will
        #  be inaccurate as  one deletion record could link to several child records.
        # join the deletion log to the childs parent id column to get a count of the
        # number of child records deleted.
        master_schema_sheet = self.schema.get_schema_loaded_sheet(self.master_sheet)
        if master_schema_sheet is not None:
            if (
                master_schema_sheet.parent_sheet is not None
                and master_schema_sheet.parent_linking_column is not None
                and self.master_deletion_log is not None
            ):
                master_filter_loaded_sheet = data.get_loaded_sheet(self.master_deletion_log)
                if master_filter_loaded_sheet is not None:
                    result, data_sheet_ids = get_data_sheet_id(
                        schema=self.schema,
                        sheet_name=self.master_deletion_log,
                        loaded_sheet=master_filter_loaded_sheet,
                        rule=self.name,
                    )

                    if result:
                        results.append(result)
                        return results
                    data_sheet_ids = data_sheet_ids[0]

                    deleted_data_count = master_filter_loaded_sheet.data.join(
                        other=data_loaded_sheets[self.master_sheet].data,
                        left_on=data_sheet_ids.data_column_name,
                        right_on=master_schema_sheet.parent_linking_column,
                        how="inner",
                    ).n_unique()
                    child_counts.append(
                        ChildCounts(
                            sheet_name=self.master_deletion_log,
                            row_count=deleted_data_count,
                        )
                    )

        master_data_count = data_loaded_sheets[self.master_sheet].data.height

        for sheet in self.child_sheets:
            child_counts.append(
                ChildCounts(sheet_name=sheet, row_count=data_loaded_sheets[sheet].data.height)
            )

        child_sum = sum([item.row_count for item in child_counts])
        missing_rows: int = abs(child_sum - master_data_count)
        if missing_rows > 0:
            child_message = " and ".join(
                [f"{item.sheet_name} ({item.row_count})" for item in child_counts]
            )
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"Sum of row counts for sheets {child_message} does not"
                    f" equal {self.master_sheet} rows ({master_data_count})."
                    f" The difference is {missing_rows}.",
                    severity=SeverityLevel.ERROR,
                )
            )

        return results
