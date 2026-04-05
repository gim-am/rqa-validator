import fastexcel
import polars as pl
from pathlib import Path
from typing import List
from ..models.schema import  DatasetSchema, SheetMapping



class ExcelLoader:
    def __init__(self, schema_config: DatasetSchema):
        self.schema = schema_config

    def load(self, filepath: Path) -> tuple[dict, list]:
        """Load matching sheets from Excel file."""
        all_sheets = fastexcel.read_excel(filepath).sheet_names
        loaded_sheets = {}
        unloaded_sheets = []
        unexpected_sheets = []
        
        for sheet_name in all_sheets:
            if self._should_load_sheet(sheet_name):
                df: pl.DataFrame = pl.read_excel(source=filepath, sheet_name=sheet_name)
                mapped_name = self._get_mapped_name(sheet_name, self.schema.loaded_sheets)

                loaded_sheets[mapped_name] = {"data": df, "original_sheet_name": sheet_name}
            elif self._should_ignore_sheet(sheet_name):
                # unexpected sheet
                mapped_name = self._get_mapped_name(sheet_name, self.schema.unloaded_sheets)
                unloaded_sheets.append(mapped_name)
            else:
                unexpected_sheets.append(sheet_name)
            
        
        return loaded_sheets, unloaded_sheets, unexpected_sheets
    
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
    