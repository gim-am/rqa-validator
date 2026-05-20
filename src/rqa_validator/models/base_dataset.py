import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..models.base import ProcessValueMap, SchemaColumnMap, SchemaSheetMap
from ..validators.base import BaseValidator


@dataclass
class BaseDatasetSchema:
    dataset_type: str = ""
    # sheets that have to be loaded and used for further validation
    schema_loaded_sheets: list[SchemaSheetMap] = field(default_factory=list)
    # sheets that should exist but dont need to be loaded
    schema_unloaded_sheets: list[SchemaSheetMap] = field(default_factory=list)

    def get_schema_loaded_sheet(self, sheet_name: str) -> SchemaSheetMap | None:
        """Gets the details and data for a loaded sheet if it exists.

        Args:
            sheet_name (str): Schema sheets to be searched for

        Returns:
            LoadedSheet | None: Loaded sheet details if found
        """
        for sheet in self.schema_loaded_sheets:
            if sheet.standard_name == sheet_name:
                return sheet
        return None

    def get_loaded_sheets_standard_names(self) -> list[str]:
        """Gets all the standard names for all the loaded sheets."""
        return [item.standard_name for item in self.schema_loaded_sheets]

    def get_unloaded_sheets_standard_names(self) -> list[str]:
        """Gets all the standard names for all the unloaded sheets."""
        return [item.standard_name for item in self.schema_unloaded_sheets]

    def get_all_sheet_names(self) -> list[str]:
        """Gets all sheet names, including alternate names

        Returns:
            List[List[str]]: list of all sheet names
        """
        sheet_names = [item.combine_sheet_names() for item in self.schema_loaded_sheets]
        sheet_names.extend([item.combine_sheet_names() for item in self.schema_unloaded_sheets])

        return list(itertools.chain.from_iterable(sheet_names))

    def get_sheet_column_standard_names(self, sheet_name: str) -> list[str] | None:
        """gets all the column standard names for a sheet."""
        sheet = self.get_schema_loaded_sheet(sheet_name)
        if sheet is not None:
            return sheet.get_column_standard_names()

    def get_schema_unloaded_sheet(self, sheet_name: str) -> SchemaSheetMap | None:
        """Gets the details and data for an unloaded sheet if it exists.

        Args:
            sheet_name (str): Schema sheets to be searched for

        Returns:
            LoadedSheet | None: Loaded sheet details if found
        """
        for sheet in self.schema_unloaded_sheets:
            if sheet.standard_name == sheet_name:
                return sheet
        return None

    def add_loaded_sheet(self, sheet: SchemaSheetMap) -> SchemaSheetMap | None:
        """Adds a sheet to schema_loaded_sheets if the standard_name provided
        does not exist.

        If the name exists within alternate_names then the schema prevalidation
        process will detect it and report an error.

        Returns None if a sheet with the same standard_name already exists


        Args:
            sheet (SheetMapping): sheet to be added

         Returns:
            SheetMapping | None: the new sheet or None
        """
        if self.get_schema_loaded_sheet(sheet.standard_name) is None:
            self.schema_loaded_sheets.append(sheet)
            return sheet

    def add_unloaded_sheet(self, sheet: SchemaSheetMap) -> SchemaSheetMap | None:
        """Adds a sheet to schema_unloaded_sheets if the standard_name provided
        does not exist.

        If the name exists within alternate_names then the schema prevalidation
        process will detect it and report an error.

        Returns None if a sheet with the same standard_name already exists

        Args:
            sheet (SheetMapping): sheet to be added

         Returns:
            SheetMapping | None: the new sheet or None

        """
        if self.get_schema_unloaded_sheet(sheet.standard_name) is None:
            self.schema_unloaded_sheets.append(sheet)
            return sheet

    def add_mandatory_column_to_sheet(
        self, sheet_standard_name: str, column: SchemaColumnMap
    ) -> SchemaSheetMap | None:
        """Adds a mandatory column to an existing sheet.
           If:
            - the sheet does not exist
            - the column already exists (based on standard_name)
            then None will be returned


        Args:
            sheet_standard_name (str): sheet where column is to be added
            column (ColumnMapping): column to be added

        Returns:
            SheetMapping | None: the sheet with the new column added or None
        """
        sheet = self.get_schema_loaded_sheet(sheet_standard_name)
        if sheet is not None:
            sheet.add_mandatory_column(column)
            return sheet


@dataclass
class DefaultDatasetSchema(BaseDatasetSchema):
    schema_loaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuid", "X_uuid"],
                        is_unique=True,
                    ),
                    SchemaColumnMap(
                        standard_name="consent",
                        alternate_names=[],
                        process_values=[
                            ProcessValueMap(
                                process_name="consent_check_validation", values=["yes", "oui"]
                            )
                        ],
                    ),
                ],
            ),
            SchemaSheetMap(
                standard_name="clean_data",
                alternate_names=["clean_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuid", "X_uuid"],
                        is_unique=True,
                    ),
                    #  SchemaColumnMap(standard_name="pop_group",
                    #                alternate_names=["pop_group"]),
                    #  SchemaColumnMap(standard_name="weight",
                    #                alternate_names=["weight"]),
                    #  SchemaColumnMap(standard_name="person_id",
                    #                alternate_names=["person_id"])
                ],
            ),
            SchemaSheetMap(
                standard_name="deletion_log",
                alternate_names=["deletion_log"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid", alternate_names=["X_uuid"], is_unique=True
                    ),
                ],
            ),
            SchemaSheetMap(
                standard_name="cleaning_log",
                alternate_names=["clog_logbook"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["x_uuid"]),
                    SchemaColumnMap(standard_name="old_value"),
                    SchemaColumnMap(standard_name="new_value"),
                    SchemaColumnMap(
                        standard_name="change_type",
                        alternate_names=["changed"],
                        process_values=[
                            ProcessValueMap(
                                process_name="cleaning_log_validation",
                                values=["yes", "change_response", "blank_response"],
                            )
                        ],
                    ),
                    SchemaColumnMap(standard_name="question"),
                ],
            ),
            SchemaSheetMap(
                standard_name="kobo_survey",
                alternate_names=["survey"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="type",
                        process_values=[
                            ProcessValueMap(
                                process_name="data_type_numeric_check",
                                values=["integer", "decimal"],
                            ),
                            ProcessValueMap(
                                process_name="data_type_temporal_check", values=["date"]
                            ),
                        ],
                    ),
                    SchemaColumnMap(standard_name="name"),
                ],
            ),
            SchemaSheetMap(
                standard_name="kobo_choices",
                alternate_names=["choices"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="list_name"),
                    SchemaColumnMap(standard_name="name"),
                ],
            ),
        ]
    )
    schema_unloaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            SchemaSheetMap(standard_name="read_me", alternate_names=["read.me", "read me"]),
            SchemaSheetMap(
                standard_name="sampling_info",
                alternate_names=["sampling_info"],
                required=False,
            ),
            SchemaSheetMap(standard_name="variable_tracker", alternate_names=["variable_tracker"]),
            SchemaSheetMap(
                standard_name="enumerator_performance_log",
                alternate_names=["enumerator_performance_log"],
                required=False,
            ),
        ]
    )


@dataclass
class DynamicDatasetSchema(BaseDatasetSchema):
    schema_loaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            SchemaSheetMap(
                standard_name="deletion_log",
                alternate_names=["deletion_log"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid", alternate_names=["X_uuid"], is_unique=True
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="kobo_survey",
                alternate_names=["survey"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="type",
                        process_values=[
                            ProcessValueMap(
                                process_name="data_type_numeric_check",
                                values=["integer", "decimal"],
                            ),
                            ProcessValueMap(
                                process_name="data_type_temporal_check", values=["date"]
                            ),
                        ],
                    ),
                    SchemaColumnMap(standard_name="name"),
                ],
            ),
            SchemaSheetMap(
                standard_name="kobo_choices",
                alternate_names=["choices"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="list_name"),
                    SchemaColumnMap(standard_name="name"),
                ],
            ),
        ]
    )
    schema_unloaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            SchemaSheetMap(standard_name="read_me", alternate_names=["read.me", "read me"]),
            SchemaSheetMap(
                standard_name="sampling_info",
                alternate_names=["sampling_info"],
                required=False,
            ),
            SchemaSheetMap(standard_name="variable_tracker", alternate_names=["variable_tracker"]),
            SchemaSheetMap(
                standard_name="enumerator_performance_log",
                alternate_names=["enumerator_performance_log"],
                required=False,
            ),
        ]
    )


class BaseDataset(ABC):
    @abstractmethod
    def get_schema() -> BaseDatasetSchema:
        pass

    @abstractmethod
    def get_validators() -> list[BaseValidator]:
        pass

    # TODO: add list of base validators here and use this in child
    # classes as a default list
