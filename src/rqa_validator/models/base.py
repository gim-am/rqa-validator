from dataclasses import dataclass, field

import polars as pl

from ..common.list_matching import add_to_list, is_in_list, unique_list


@dataclass
class DynamicSheetMatching:
    data: pl.DataFrame
    id_column: str | None
    id_column_set: set | None
    classification: str | None = None
    log_type: str | None = None
    parent_sheet: str | None = None
    parent_linking_column: str | None = None
    children: list[str] = field(default_factory=list)
    linked_cleaning_log: str | None = None
    linked_raw_sheet: str | None = None
    linked_clean_sheet: str | None = None
    log_id_column: str | None = None


@dataclass
class ProcessValueMap:
    """Values expexted in a column required for a validation process"""

    process_name: str
    values: list = field(default_factory=list)


@dataclass
class SchemaColumnMap:
    standard_name: str
    alternate_names: list[str] = field(default_factory=list)
    is_unique: bool = False
    process_values: list[ProcessValueMap] = field(default_factory=list)

    def combine(self) -> list[str]:
        """returns a unique list of column names and alternate names"""
        return add_to_list(self.standard_name, self.alternate_names)

    def get_process_values(self, process_name: str):
        for item in self.process_values:
            if item.process_name == process_name:
                return item


@dataclass
class SchemaSheetMap:
    standard_name: str
    alternate_names: list[str] = field(default_factory=list)
    mandatory_columns: list[SchemaColumnMap] = field(default_factory=list)
    parent_sheet: str | None = None
    parent_linking_column: str | None = None

    required: bool = True

    def get_column(self, column_name: str) -> SchemaColumnMap | None:
        """Returns a column from mandatory_columns if a name is matched."""
        for column in self.mandatory_columns:
            if column.standard_name == column_name:
                return column

    def get_column_standard_names(self):
        """Gets the standard names for all mandatory columns."""
        return [item.standard_name for item in self.mandatory_columns]

    def get_unique_columns(self) -> list[SchemaColumnMap]:
        """Gets all the columns markes as unique"""
        return [column for column in self.mandatory_columns if column.is_unique]

    def matches(self, sheet_name: str) -> bool:
        """checks if a sheet name is part of the schema (including alternate names)"""
        return is_in_list(sheet_name, self.combine_sheet_names())

    def combine_column_names(self, return_unique_list: bool = True) -> list[str]:
        """Creates a unique list of mandatory and unique column name options

        Args:
            include_unique_columns (bool, optional): Include unique columns in the results. Defaults to True.
            return_unique_list (bool, optional): return a list of unique values. Defaults to True.

        Returns:
            List[str]: returns a list of column names and alternate names for a sheet
        """
        column_list: list[str] = []
        for column in self.mandatory_columns:
            column_list.extend(column.combine())

        # this list may have dupliaces if columns share names or laternate names
        if return_unique_list:
            return unique_list(column_list)
        else:
            return column_list

    def combine_sheet_names(self) -> list[str]:
        """combines standard_name and alternate_names into one list checking
        standard_name is not in alternate_names list

        Returns:
            List[str]: combined list of unique items
        """
        return add_to_list(self.standard_name, self.alternate_names)

    def add_mandatory_column(self, column: SchemaColumnMap) -> SchemaColumnMap | None:
        """Adds a column to mandatory_columns if the standard_name provided
        does not exist.

        If the name exists within alternate_names then the schema prevalidation
        process will detect it and report an error.

        Returns None if a column with the same standard_name already exists

        Returns:
            ColumnMapping | None: the new column or None
        """

        if self.get_column(column.standard_name) is None:
            self.mandatory_columns.append(column)
            return column

    def add_alternate_name_to_column(self, column_name: str, name: str):
        """adds a new alternate name to a mandatory column.

        Args:
            column_name (str): standard name of existing mandatory column
            name (str): name to add to alternate names list
        """
        for idx, column in enumerate(self.mandatory_columns):
            if column.standard_name == column_name:
                self.mandatory_columns[idx].alternate_names = add_to_list(
                    name, self.mandatory_columns[idx].alternate_names
                )

    def add_alternate_name_to_sheet(self, name: str):
        """Adds a new alternate name to the sheet

        Args:
            name (str): name to add to alternate names list
        """
        self.alternate_names = add_to_list(name, self.alternate_names)
