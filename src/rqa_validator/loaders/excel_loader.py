from dataclasses import dataclass, field

import fastexcel
import polars as pl
from pathlib import Path
from typing import List

# from ..validators.base import ValidationResult
from ..models.schema import  BaseDatasetSchema, SheetMapping

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
        # self.results: List[ValidationResult] = []

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
            if (mapped_name := self._match_sheet(sheet_name, self.schema.schema_loaded_sheets)):
                # sheets that are expected and loaded for further data validation
                df: pl.DataFrame = pl.read_excel(source=filepath, sheet_name=sheet_name)
                # TODO: check for duplicate column names. difficult as they are renames on load
                df = df.rename(str.lower)
                                
                data.loaded_sheets.append(LoadedSheet(mapped_name=mapped_name,
                                                      original_name=sheet_name,
                                                      data=df,
                                                      columns=df.columns))                

            elif (mapped_name := self._match_sheet(sheet_name, self.schema.schema_unloaded_sheets)):
                # sheets that are expected but dont need to be loaded
                data.unloaded_sheets.append(mapped_name)
            else:
                # unexpected sheets
                data.unexpected_sheets.append(sheet_name)

        return data
    

    def _match_sheet(self, sheet_name: str, schema_sheets: List[SheetMapping]):
        # ret_value: str = str()
        matched_values: List[str] = []
        for sheet_config in schema_sheets:
            if sheet_config.matches(sheet_name):
                matched_values.append(sheet_config.standard_name)

        # if not matched_values:
            # do fuzzy matching

        if len(matched_values) == 1:
            return matched_values[0]
        # else:




    
    
    