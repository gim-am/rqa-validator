from dataclasses import dataclass, field
from typing import List


from ..common.list_matching import is_in_list, add_to_list, unique_list

@dataclass
class ColumnMapping:
    standard_name: str    
    alternate_names: List[str] = field(default_factory=list) 
    is_unique: bool = False

    def combine(self) -> List[str]:
        """returns a unique list of column names and alternate names"""
        return add_to_list(self.standard_name, self.alternate_names)


@dataclass
class SheetMapping:
    standard_name: str 
    alternate_names: List[str] 
    mandatory_columns: List[ColumnMapping] = field(default_factory=list)
    required: bool = True  
    
    
    def get_unique_columns(self):
        return [column for column in self.mandatory_columns if column.is_unique]
    
    def matches(self, sheet_name: str)  -> bool:
        """checks if a sheet name is part of the schema (including alternate names)"""
        return is_in_list(sheet_name, self.combine_sheet_names())  
    
    def combine_column_names(self, return_unique_list: bool = True) -> List[str]:
        """Creates a unique list of mandatory and unique column name options

        Args:
            include_unique_columns (bool, optional): Include unique columns in the results. Defaults to True.
            return_unique_list (bool, optional): return a list of unique values. Defaults to True.

        Returns:
            List[str]: returns a list of column names and alternate names for a sheet
        """
        column_list: List[str] = []
        for column in self.mandatory_columns:
            column_list.extend(column.combine())
        
        # this list may have dupliaces if columns share names or laternate names
        if return_unique_list:
            return unique_list(column_list)
        else:
            return column_list
        
    def combine_sheet_names(self) -> List[str]:
        """combines standard_name and alternate_names into one list checking 
        standard_name is not in alternate_names list

        Returns:
            List[str]: combined list of unique items
        """
        return add_to_list(self.standard_name, self.alternate_names)






