from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import List, Optional

from ..validators.base import BaseValidator
from ..common.matching import is_in_list, add_to_list, combine_lists, unique_list

@dataclass
class ColumnMapping:
    standard_name: str    
    alternate_names: List[str] = field(default_factory=list) 
    # matched_name: str = str()

    def combine(self) -> List[str]:
        """returns a unique list of column names and alternate names"""
        return add_to_list(self.standard_name, self.alternate_names)


@dataclass
class SheetMapping:
    standard_name: str
    alternate_names: List[str] 
    # matched_name: str = str() 
    mandatory_columns: List[ColumnMapping] = field(default_factory=list)
    required: bool = True  
    # unique columns are included in the mandatory_column check rule
    unique_columns: Optional[ColumnMapping] = None 
    
    def matches(self, sheet_name: str)  -> bool:
        """checks if a sheet name is part of the schema (including alternate names)"""
        return is_in_list(sheet_name, self.combine_sheet_names())  
    
    def combine_column_names(self, include_unique_columns: bool = True, return_unique_list: bool = True) -> List[str]:
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

        if include_unique_columns:
            return combine_lists(self.unique_columns.combine(), column_list, return_unique_list)
        else:
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


@dataclass
class BaseDatasetSchema:
    dataset_type: str 
    # sheets that have to be loaded and used for further validation
    schema_loaded_sheets: List[SheetMapping]= field(default_factory=list)
    # sheets that should exist but dont need to be loaded
    schema_unloaded_sheets: List[SheetMapping]   = field(default_factory=list) 

    def get_schema_sheet(self, sheet_name: str)  -> SheetMapping | None:
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

   
@dataclass()
class DefaultDatasetSchema(BaseDatasetSchema):

    schema_loaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        unique_columns= ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"])),
        SheetMapping(standard_name= "variable_tracker", 
                        alternate_names =["variable_tracker"]),
        SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns = [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"]),
                                             ColumnMapping(standard_name="stratum",
                                                           alternate_names=["stratum"]),
                                             ColumnMapping(standard_name="pop_group",
                                                           alternate_names=["pop_group"]),
                                             ColumnMapping(standard_name="weight",
                                                           alternate_names=["weight"]),
                                             ColumnMapping(standard_name="person_id",
                                                           alternate_names=["person_id"])
                                            ],
                        unique_columns= ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"])),
        SheetMapping(standard_name= "deletion_log", 
                        alternate_names =["deletion_log"],                        
                        unique_columns= ColumnMapping(standard_name="uuid") ),
        SheetMapping(standard_name="cleaning_log", 
                        alternate_names=["cleaning_log"]),                               
    ])
    schema_unloaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name="read_me", 
                        alternate_names= ["read_me"]),
        SheetMapping(standard_name="kobo_survey", 
                        alternate_names= ["kobo_survey"]),
        SheetMapping(standard_name= "kobo_choices", 
                        alternate_names =["kobo_choices"]),        
        SheetMapping(standard_name="sampling_info", 
                        alternate_names=["sampling_info"], 
                        required=False),
        SheetMapping(standard_name="enumerator_performance_log", 
                        alternate_names=["enumerator_performance_log"], 
                        required=False)
    ])


class BaseDataset(ABC):
    @abstractmethod
    def get_schema() -> BaseDatasetSchema:
        pass

    @abstractmethod
    def get_validators() -> List[BaseValidator]:
        pass




