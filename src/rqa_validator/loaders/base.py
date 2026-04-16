from dataclasses import dataclass, field
from typing import List
import polars as pl

@dataclass
class ColumnMap():
    schema_column_name:str
    data_column_name:str


@dataclass
class LoadedSheet:
    schema_sheet_name:str
    data_sheet_name: str
    data: pl.DataFrame
    # this operation is ran numerous times so might as well store it once here
    data_columns: List[str] = field(default_factory=list)
    column_map: List[ColumnMap] = field(default_factory=list)

    def get_column_map(self, search_column: str) -> ColumnMap | None:
        """Searches if a schema column name was mapped during data load.
        Returns a column mapping if found

        Args:
            search_column (str): schema column to search for

        Returns:
            ColumnMap | None: a column map between scheema column and 
            excel sheet column
        """
        for column in self.column_map:
            if  column.schema_column_name == search_column:
                return column
