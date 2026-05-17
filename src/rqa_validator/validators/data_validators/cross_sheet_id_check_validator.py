import polars as pl

from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult
from ..data_helpers import (
    get_data_loaded_sheet,
    get_data_loaded_sheets,
    get_data_sheet_ids,
    get_id_linking_columns,
)


class CrossSheetIdCheck(BaseValidator):
    def __init__(
        self,
        schema: BaseDatasetSchema,
        master_sheet: str = "raw_data",
        child_sheets: list[str] = ["clean_data", "deletion_log", "cleaning_log"],
        is_in: bool = True,
    ):
        """Checks to see if ids from child sheet/s are present in a master/parent sheet

        Args:
            schema (BaseDatasetSchema): dataset schema
            master_sheet (str, optional): Sheet to make sure that child ids are in.
                Defaults to 'raw_data'.
            child_sheets (List, optional): Sheet/s to make sure that ids are in
                master_sheet. Defaults to ['clean_data', 'deletion_log', 'cleaning_log']
            is_in (bool, optional): determins if the child ids should (true) or
                should not (false) be in the matser sheet
        """
        self.master_sheet = master_sheet
        self.child_sheets = child_sheets
        self.schema = schema
        self.is_in = is_in

    @property
    def name(self) -> str:
        return "CrossSheetIdCheck"

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
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
        results: list[ValidationResult] = []

        if self.is_in:
            join_type = "anti"
        else:
            join_type = "semi"

        result, data_loaded_sheets = get_data_loaded_sheets(
            data=data, sheet_names=[self.master_sheet], rule=self.name
        )

        if result:
            results.extend(result)
            return results

        result, data_sheet_ids = get_data_sheet_ids(
            schema=self.schema,
            data={self.master_sheet: data_loaded_sheets[self.master_sheet]},
            rule=self.name,
        )

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

            if child_loaded_sheet.data.height < 1:
                # no data in sheet. eg empty deletion log
                continue

            result, child_data_id_columns, master_id_columns = get_id_linking_columns(
                schema=self.schema,
                data_loaded_sheets=data_loaded_sheets | {sheet: child_loaded_sheet},
                source_sheet=sheet,
                target_sheet=self.master_sheet,
                rule=self.name,
            )
            if child_data_id_columns is None or master_id_columns is None:
                results.extend(result)
                return results
            assert child_data_id_columns is not None
            assert master_id_columns is not None

            # filter id column. should only actually filter anything if the sheet
            # is a cleaning log sheet as it contains ids from multiple
            # clean data sheets (loops)
            missing_ids = (
                child_loaded_sheet.data.select(child_data_id_columns.data_column_name)
                .filter(
                    (
                        pl.col(child_data_id_columns.data_column_name)
                        .cast(pl.Utf8)
                        .str.strip_chars(" ")
                        .is_not_null()
                    )
                    & (
                        pl.col(child_data_id_columns.data_column_name)
                        .cast(pl.Utf8)
                        .str.strip_chars(" ")
                        != ""
                    )
                )
                .join(
                    other=data_loaded_sheets[self.master_sheet].data.select(
                        master_matching_columns.data_column_name
                    ),
                    how=join_type,
                    left_on=child_data_id_columns.data_column_name,
                    right_on=master_matching_columns.data_column_name,
                )
                .to_series()
                .to_list()
            )
            if missing_ids:
                results.append(
                    ValidationResult(
                        rule=self.name,
                        message="Id values for sheet"
                        f" '{child_loaded_sheet.data_sheet_name}' and column"
                        f" '{child_data_id_columns.data_column_name}' were not found in"
                        f" sheet '{data_loaded_sheets[self.master_sheet].data_sheet_name}'"
                        f" column '{master_matching_columns.data_column_name}'."
                        "Check output for details. ",
                        severity=SeverityLevel.ERROR,
                        sheet_name=child_loaded_sheet.data_sheet_name,
                        column_name=child_data_id_columns.data_column_name,
                        details={child_data_id_columns.data_column_name: missing_ids},
                    )
                )

        return results
