import polars as pl

from ...common.schema_matching import get_matching_unique_columns
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult
from ...validators.helpers import (
    get_data_loaded_sheet,
    get_data_loaded_sheets,
    get_data_sheet_ids,
    get_matching_id_columns,
    get_matching_id_columns_alt,
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

            # gets ids from a child sheet that are not present in a master sheet

            # this process assumes that:
            # if both sheets have a unique column then these should be compared
            # if one sheet does not have a unique id column then a match is attempted
            #   based on schema name.

            child_matching_columns = get_matching_unique_columns(
                self.schema, child_loaded_sheet, sheet
            )

            if not child_matching_columns:
                # some sheets will have a non unique uuid column
                # so try to match based on name

                result, child_matching_columns = get_matching_id_columns(
                    child_loaded_sheet.column_map,
                    child_loaded_sheet.data_sheet_name,
                    [master_matching_columns],
                    self.master_sheet,
                    self.name,
                )
                if result is not None:
                    result, child_data_id_columns, master_id_columns = (
                        get_matching_id_columns_alt(
                            child_loaded_sheet.column_map,
                            child_loaded_sheet.data_sheet_name,
                            [master_matching_columns],
                            self.master_sheet,
                            self.name,
                        )
                    )
                    if result is not None:
                        results.append(result)
                        continue
                    else:
                        child_data_id_columns = child_data_id_columns[0]
                        master_id_columns = master_id_columns[0]
                else:
                    child_data_id_columns = child_matching_columns[0][0]
                    master_id_columns = child_matching_columns[0][1]
            else:
                child_data_id_columns = child_matching_columns[0]
                master_id_columns = child_matching_columns[0]

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
                        message=f"Id values for sheet \
                            {child_loaded_sheet.data_sheet_name} and column \
                            {child_data_id_columns.data_column_name} were not found in\
                          sheet {data_loaded_sheets[self.master_sheet].data_sheet_name}\
                             column {master_matching_columns.data_column_name}.\
                            Check output for details. ",
                        severity=SeverityLevel.ERROR,
                        sheet_name=child_loaded_sheet.data_sheet_name,
                        column_name=child_data_id_columns.data_column_name,
                        details={child_data_id_columns.data_column_name: missing_ids},
                    )
                )

        return results
