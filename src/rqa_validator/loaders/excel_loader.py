from dataclasses import dataclass, field

import fastexcel
import polars as pl
from pathlib import Path
from typing import List
from ..models.schema import  BaseDatasetSchema

@dataclass
class LoadedSheet:
    mapped_name:str
    original_name: str
    data: pl.DataFrame
    # this operation is ran numerous times so might as well store it once here
    columns: List[str]

@dataclass
class ExcelLoaderData:
    loaded_sheets: List[LoadedSheet] = field(default_factory=list)
    unloaded_sheets = []
    unexpected_sheets = []

    def get_loaded_sheet_mapped_names(self) -> List[str]:
        """Gets all the standard names for the loaded excel sheets

        Returns:
            List[str]: List of sheet names.
        """
        return [sheet.mapped_name for sheet in self.loaded_sheets]
    
    def get_loaded_sheet(self, sheet_name: str)  -> LoadedSheet | None:
        """Gets the details and data for a loaded sheet if it exists.

        Args:
            sheet_name (str): Excel sheets to be searched for

        Returns:
            LoadedSheet | None: Loaded sheet details if found
        """
        for sheet in self.loaded_sheets:
            if sheet.mapped_name == sheet_name:
                return sheet
        return None
    

class ExcelLoader:

    def __init__(self, schema_config: BaseDatasetSchema):
        self.schema = schema_config

    def load(self, filepath: Path)  -> ExcelLoaderData:
        """Loads an excel file, does some checking and sorting of the sheets.

        Args:
            filepath (Path): Filepath of excel file. Might change for api call.

        Returns:
            ExcelLoaderData: class that contains the loaded data, sheets etc.
        """
        # get a list of excel sheet names
        all_sheets = fastexcel.read_excel(filepath).sheet_names
        # lower sheet names for easier comparison later
        all_sheets = list(map(str.lower, all_sheets))
        
        data = ExcelLoaderData()
        
        for sheet_name in all_sheets:
            if (mapped_name := self._should_load_sheet(sheet_name)):
                # sheets that are expected and loaded for further data validation
                df: pl.DataFrame = pl.read_excel(source=filepath, sheet_name=sheet_name)
                # TODO: check for duplicate column names. difficult as they are renames on load
                df = df.rename(str.lower)
                                
                data.loaded_sheets.append(LoadedSheet(mapped_name=mapped_name,
                                                      original_name=sheet_name,
                                                      data=df,
                                                      columns=df.columns))                

            elif (mapped_name := self._should_ignore_sheet(sheet_name)):
                # sheets that are expected but dont need to be loaded
                data.unloaded_sheets.append(mapped_name)
            else:
                # unexpected sheets
                data.unexpected_sheets.append(sheet_name)

        return data
    
    def _should_load_sheet(self, sheet_name: str)  -> str | None:
        """Check if sheet name matches any configured/expected names
            that are to be loaded.

        Args:
            sheet_name (str): Sheet name to be checked

        Returns:
            str | None: standard name if a match is made
        """
        for sheet_config in self.schema.loaded_sheets:
            if sheet_config.matches(sheet_name):
                return sheet_config.standard_name
    
    def _should_ignore_sheet(self, sheet_name: str)  -> str | None:
        """Check if sheet name matches any configured names
            that should be ignored/not loaded.

        Args:
            sheet_name (str): Sheet name to be checked

        Returns:
            str | None: standard name if a match is made
        """
        for sheet_config in self.schema.unloaded_sheets:
            if sheet_config.matches(sheet_name):
                return sheet_config.standard_name
    