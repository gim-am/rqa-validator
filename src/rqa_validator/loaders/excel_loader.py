from dataclasses import dataclass

import fastexcel
import polars as pl
from pathlib import Path
from typing import List
from ..models.schema import  BaseDatasetSchema, SheetMapping

@dataclass
class LoadedSheet:
    mapped_name:str
    original_name: str
    data: pl.DataFrame

class ExcelLoaderData:
    loaded_sheets: List[LoadedSheet] = []
    unloaded_sheets = []
    unexpected_sheets = []

    def get_loaded_sheet_mapped_names(self) -> List[str]:
        return [sheet.mapped_name for sheet in self.loaded_sheets]
    
    def get_loaded_sheet(self, sheet_name: str)  -> LoadedSheet | None:

        for sheet in self.loaded_sheets:
            if sheet.mapped_name == sheet_name:
                return sheet
        return None
    

class ExcelLoader:
    def __init__(self, schema_config: BaseDatasetSchema):
        self.schema = schema_config

    def load(self, filepath: Path)  -> ExcelLoaderData:
        """Load matching sheets from Excel file."""
        all_sheets = fastexcel.read_excel(filepath).sheet_names
        all_sheets = list(map(str.lower, all_sheets))
        
        data = ExcelLoaderData()
        
        for sheet_name in all_sheets:
            if self._should_load_sheet(sheet_name):
                df: pl.DataFrame = pl.read_excel(source=filepath, sheet_name=sheet_name)
                # TODO: check for duplicate column names. difficult as they are renames on load
                df = df.rename(str.lower)
                
                mapped_name = self._get_mapped_name(sheet_name, self.schema.loaded_sheets)
                
                data.loaded_sheets.append(LoadedSheet(mapped_name=mapped_name,
                                                      original_name=sheet_name,
                                                      data=df))                

            elif self._should_ignore_sheet(sheet_name):
                # unexpected sheet
                mapped_name = self._get_mapped_name(sheet_name, self.schema.unloaded_sheets)
                data.unloaded_sheets.append(mapped_name)
            else:
                data.unexpected_sheets.append(sheet_name)

        return data
    
    def _get_mapped_name(self, sheet_name: str, sheets: List[SheetMapping]) -> str:
        """Get standardized name for sheet."""
        for sheet_config in sheets:
            if sheet_name in sheet_config.names:
                return sheet_config.standard_name
        return sheet_name
    
    def _should_load_sheet(self, sheet_name: str) -> bool:
        """Check if sheet name matches any configured names."""
        for sheet_config in self.schema.loaded_sheets:
            if sheet_config.matches(sheet_name):
                return sheet_config.standard_name
    
    def _should_ignore_sheet(self, sheet_name: str) -> bool:
        """Check if sheet name matches any configured names."""
        for sheet_config in self.schema.unloaded_sheets:
            if sheet_config.matches(sheet_name):
                return sheet_config.standard_name
    