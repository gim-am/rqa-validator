from dataclasses import dataclass, field
from typing import List
import polars as pl


@dataclass
class DataColumnMap:
    schema_column_name: str
    data_column_name: str


@dataclass
class DataSheetMap:
    schema_sheet_name: str
    data_sheet_name: str
    data: pl.DataFrame = field(default_factory=pl.DataFrame)
    # this operation is ran numerous times so might as well store it once here
    data_columns: List[str] = field(default_factory=list)
    column_map: List[DataColumnMap] = field(default_factory=list)

    def get_column_map(self, search_column: str) -> DataColumnMap | None:
        """Searches if a schema column name was mapped during data load.
        Returns a column mapping if found

        Args:
            search_column (str): schema column to search for

        Returns:
            ColumnMap | None: a column map between scheema column and
            excel sheet column
        """
        for column in self.column_map:
            if column.schema_column_name == search_column:
                return column

    def add_column_map(self, column_map: DataColumnMap):
        self.column_map.append(column_map)

    def set_column_map(self, column_maps: List[DataColumnMap]):
        self.column_map = column_maps
