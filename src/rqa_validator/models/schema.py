from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import List, Optional

from ..validators.base import BaseValidator

@dataclass
class ColumnMapping:
    standard_name: str    
    alternate_names: List[str] = field(default_factory=list) 
    # matched_name: str = str()

    def combine(self) -> List[str]:
        ret_list: List[str] = []
        if not self.alternate_names :
            ret_list = [self.standard_name]
        elif self.standard_name not in self.alternate_names:
            ret_list = self.alternate_names
            ret_list.append(self.standard_name)
        else:
            ret_list = self.alternate_names

        return ret_list

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
        return sheet_name in self.combine_sheet_names()  
    
    def combine_column_names(self) -> List[str]:
        """Creates a unique list of mandatory and unique column name options

        Returns:
            List[str]: _description_
        """
        ret_list: List[str] = []
        column_list: List[str] = []

        if self.unique_columns is not None:
            column_list.extend(self.unique_columns.combine())

        for column in self.mandatory_columns:
            column_list.extend(column.combine())

        [ret_list.append(column) for column in column_list if column not in ret_list]

        if ret_list == [None]:
            ret_list = []

        return ret_list

    def combine_sheet_names(self) -> List[str]:
        """combines standard_name and alternate_names into one list checking 
        standard_name is not in alternate_names list

        Returns:
            List[str]: combined list
        """
        ret_list: List[str] = []
        if not self.alternate_names :
            ret_list = [self.standard_name]
        elif self.standard_name not in self.alternate_names:
            ret_list = self.alternate_names
            ret_list.append(self.standard_name)
        else:
            ret_list = self.alternate_names

        return ret_list  


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




