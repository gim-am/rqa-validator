from dataclasses import dataclass, field
from pathlib import Path

import fastexcel
import polars as pl

from ..models.base_dataset import BaseDatasetSchema
from ..validators.base import SeverityLevel, ValidationResult
from .base import (
    DataColumnMap,
    DataSheetMap,
)
from .base_excel_loader import BaseExcelLoader


@dataclass
class ExcelLoaderData:
    loaded_sheets: list[DataSheetMap] = field(default_factory=list)
    unloaded_sheets: list[DataSheetMap] = field(default_factory=list)
    unexpected_sheets: list[str] = field(default_factory=list)
    hidden_sheets: list[str] = field(default_factory=list)

    def set_column_map_for_loaded_sheet(self, sheet: str, column_maps: list[DataColumnMap]):
        loaded_sheet = self.get_loaded_sheet(sheet)
        if loaded_sheet is not None:
            loaded_sheet.set_column_map(column_maps)

    def get_loaded_sheet_mapped_names(self) -> list[str]:
        """Gets all the standard names for the loaded excel sheets

        Returns:
            List[str]: List of sheet names.
        """
        return [sheet.schema_sheet_name for sheet in self.loaded_sheets]

    def get_loaded_sheet_excel_names(self) -> list[str]:
        """Gets all the excel names for the loaded excel sheets
        that were mapped to the origianl schema.

        This is related to dynamic model creation process.

        Returns:
            List[str]: List of sheet names.
        """
        return [sheet.data_sheet_name for sheet in self.loaded_sheets if not sheet.auto_loaded]

    def get_unloaded_sheet_mapped_names(self) -> list[str]:
        """Gets all the standard names for the loaded excel sheets

        Returns:
            List[str]: List of sheet names.
        """
        return [sheet.schema_sheet_name for sheet in self.unloaded_sheets]

    def get_loaded_sheet(self, sheet_name: str) -> DataSheetMap | None:
        """Gets the details and data for a loaded sheet if it exists.

        Args:
            sheet_name (str): Excel sheets to be searched for

        Returns:
            SheetMap | None: Loaded sheet details if found
        """
        for sheet in self.loaded_sheets:
            if sheet.schema_sheet_name == sheet_name:
                return sheet
        return None

    def remove_loaded_sheet(self, sheet_name: str):
        for idx, sheet in enumerate(self.loaded_sheets):
            if sheet.schema_sheet_name == sheet_name:
                self.loaded_sheets.pop(idx)

    def get_sheet_matches(self, sheet_name: str) -> list[DataSheetMap]:
        """Gets all the sheets matched with a given schema_name.

        Args:
            sheet_name (str): Excel sheets to be searched for

        Returns:
            List[SheetMap] | None: Loaded sheet details if found
        """
        sheets: list[DataSheetMap] = []
        for sheet in self.loaded_sheets:
            if sheet.schema_sheet_name == sheet_name:
                sheets.append(sheet)

        for sheet in self.unloaded_sheets:
            if sheet.schema_sheet_name == sheet_name:
                sheets.append(sheet)

        return sheets


class ExcelLoader(BaseExcelLoader):
    def __init__(self, schema_config: BaseDatasetSchema):
        self.schema = schema_config

    def load(
        self, filepath: Path, load_all_sheets: bool = False
    ) -> tuple[ExcelLoaderData, list[ValidationResult]]:
        """Loads an excel file, does some checking and sorting of the sheets.

        Args:
            filepath (Path): Filepath of excel file. Might change for api call.
            load_all_sheets (bool): loaded all unmapped sheets. used for dynamic
                schema generation. Defaults to 'False'
        Returns:
            tuple[ExcelLoaderData,  List[ValidationResult]]:
            class that contains the loaded data, sheets etc,
            list of validation warnings

        """
        results: list[ValidationResult] = []
        # get a list of excel sheet names
        excel_file = fastexcel.read_excel(filepath)
        all_sheets = excel_file.sheet_names
        # lower sheet names for easier comparison later
        # all_sheets = list(map(str.lower, all_sheets))

        data = ExcelLoaderData()

        def _load_excel_sheet(
            excel_file: fastexcel.ExcelReader, sheet_name: str, schema_sheet_name: str | None = None
        ) -> bool:
            excel_sheet = excel_file.load_sheet(
                sheet_name, whitespace_as_null=True, skip_whitespace_tail_rows=True
            )
            # check hidden sheets
            if excel_sheet.visible != "visible":
                data.hidden_sheets.append(sheet_name)
            data_df: pl.DataFrame = excel_sheet.to_polars()
            result = self.check_duplicate_columns(data_df.columns, excel_sheet_name)
            # if there are duplicates then the rename function below will fail
            if result is not None:
                results.append(result)
                return False

            data_df = data_df.rename(str.lower)
            if schema_sheet_name is not None:
                schema_sheet = self.schema.get_schema_loaded_sheet(schema_sheet_name)
                if schema_sheet is not None:
                    column_results, column_matches = self.match_excel_columns_to_schema(
                        data_df.columns, schema_sheet
                    )
                    data.loaded_sheets.append(
                        DataSheetMap(
                            schema_sheet_name=l_mapped_name,
                            data_sheet_name=excel_sheet_name,
                            data=data_df,
                            column_map=column_matches,
                        )
                    )
                    results.extend(l_results)
                    results.extend(column_results)

                else:
                    results.append(
                        ValidationResult(
                            rule="Getting Schema Sheet",
                            message=self._(
                                "excel_loader._load_excel_sheet.sheet_not_found",
                                sheet=l_mapped_name,
                            ),
                            severity=SeverityLevel.ERROR,
                            sheet_name=l_mapped_name,
                        )
                    )
                    return False
            else:
                data.loaded_sheets.append(
                    DataSheetMap(
                        schema_sheet_name=excel_sheet_name,
                        data_sheet_name=excel_sheet_name,
                        data=data_df,
                        auto_loaded=True,
                    )
                )
            return True

        for excel_sheet_name in all_sheets:
            l_mapped_name, l_results = self.match_excel_sheet_to_schema(
                excel_sheet_name, self.schema.schema_loaded_sheets
            )
            u_mapped_name, u_results = self.match_excel_sheet_to_schema(
                excel_sheet_name, self.schema.schema_unloaded_sheets
            )

            # pre schema validation will throw error if any sheets have matching names
            # or alternate names as well as if any columns within a sheet are
            # duplicated (via names or alternate names) so there should not be
            # both l_mapped_name and u_mapped_name for literal matches options
            # 1: l_mapped_name, not l_results > literal match on loaded sheets
            # 2: u_mapped_name, not u_results > literal match on unloaded sheets
            # 3: l_mapped_name, l_results, not u_mapped_name >
            #   fuzzy match on loaded sheets
            # 4: u_mapped_name, u_results > fuzzy match on unloaded sheets
            # 5: l_mapped_name and u_mapped_name > error fuzzy matching
            # 6: not l_mapped_name, not u_mapped_name, (u_results or l_results) >
            #   error fuzzy matching
            # 7: unexpected sheet > no matching
            # load_all_sheets: loads all sheets not loaded for steps 1-6.
            #   used for dynamic schema generation

            # 5
            if l_mapped_name and l_results and u_mapped_name and u_results:
                results.append(
                    ValidationResult(
                        rule="Match excel sheeet to schema",
                        message=self._(
                            "excel_loader.load.multiple_matches", sheet=excel_sheet_name
                        ),
                        severity=SeverityLevel.INFO,
                        sheet_name=excel_sheet_name,
                    )
                )
            # 6
            elif not l_mapped_name and not u_mapped_name and (l_results or u_results):
                results.extend(l_results)
                results.extend(u_results)

            # 1 and 3
            elif l_mapped_name and (
                not l_results
                or (l_results and (not (u_mapped_name and not u_results) or not u_mapped_name))
            ):
                # sheets that are expected and loaded for further data validation
                result = _load_excel_sheet(excel_file, excel_sheet_name, l_mapped_name)
                if not result:
                    continue

            # 2, 4
            elif u_mapped_name:
                # sheets that are expected but dont need to be loaded
                data.unloaded_sheets.append(
                    DataSheetMap(
                        schema_sheet_name=u_mapped_name,
                        data_sheet_name=excel_sheet_name,
                    )
                )
                results.extend(u_results)
            else:
                if load_all_sheets:
                    result = _load_excel_sheet(excel_file, excel_sheet_name, None)
                    if not result:
                        continue
                else:
                    # 7
                    data.unexpected_sheets.append(excel_sheet_name)

        return data, results
