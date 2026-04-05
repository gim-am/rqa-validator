from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class SheetMapping:
    standard_name: str
    names: List[str]  
    
    
    def matches(self, sheet_name: str) -> bool:
        return sheet_name in self.names
    
# class LoadedSheets(SheetMapping):
#     standard_name: str
    
@dataclass
class ColumnMapping:
    # standard_name: str
    names: List[str]  


@dataclass
class DatasetSchema:
    dataset_type: str
    loaded_sheets: List[SheetMapping]
    unloaded_sheets: List[SheetMapping]    
    # expected but not loaded
    # ignored_sheets: List[SheetMapping]
    # removeable_columns: Dict[str, List[ColumnMapping]] 



