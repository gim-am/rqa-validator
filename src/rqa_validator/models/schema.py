from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import List, Optional

from ..validators.base import BaseValidator


@dataclass
class ColumnMapping:
    standard_name: str    
    names: List[str] = field(default_factory=list) 

    def combine(self) -> List[str]:
        ret_list: List[str] = []
        if not self.names :
            ret_list = [self.standard_name]
        elif self.standard_name not in self.names:
            ret_list = self.names
            ret_list.append(self.standard_name)
        else:
            ret_list = self.names

        return ret_list

@dataclass
class SheetMapping:
    standard_name: str
    names: List[str]  
    mandatory_columns: List[ColumnMapping] = field(default_factory=list)
    required: bool = True  
    # unique columns are included in the mandatory_column check rule
    unique_columns: Optional[ColumnMapping] = None 
    
    def matches(self, sheet_name: str)  -> bool:
        return sheet_name in self.names    


@dataclass
class BaseDatasetSchema:
    dataset_type: str 
    # sheets that have to be loaded and used for further validation
    loaded_sheets: List[SheetMapping]= field(default_factory=list)
    # sheets that should exist but dont need to be loaded
    unloaded_sheets: List[SheetMapping]   = field(default_factory=list) 

    def get_loaded_sheet(self, sheet_name: str)  -> SheetMapping | None:
        """Gets the details and data for a loaded sheet if it exists.

        Args:
            sheet_name (str): Schema sheets to be searched for

        Returns:
            LoadedSheet | None: Loaded sheet details if found
        """
        for sheet in self.loaded_sheets:
            if sheet.standard_name == sheet_name:
                return sheet
        return None

   
@dataclass()
class DefaultDatasetSchema(BaseDatasetSchema):

    loaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name= "raw_data", 
                        names =["raw_data"],
                        unique_columns= ColumnMapping(standard_name="uuid",
                                                           names=["uuid", "X_uuid"])),
        SheetMapping(standard_name= "variable_tracker", 
                        names =["variable_tracker"]),
        SheetMapping(standard_name= "clean_data", 
                        names =["clean_data"],
                        mandatory_columns = [ColumnMapping(standard_name="uuid",
                                                           names=["uuid", "X_uuid"]),
                                             ColumnMapping(standard_name="stratum",
                                                           names=["stratum"]),
                                             ColumnMapping(standard_name="pop_group",
                                                           names=["pop_group"]),
                                             ColumnMapping(standard_name="weight",
                                                           names=["weight"]),
                                             ColumnMapping(standard_name="person_id",
                                                           names=["person_id"])
                                            ],
                        unique_columns= ColumnMapping(standard_name="uuid",
                                                           names=["uuid", "X_uuid"])),
        SheetMapping(standard_name= "deletion_log", 
                        names =["deletion_log"],                        
                        unique_columns= ColumnMapping(standard_name="uuid") ),
        SheetMapping(standard_name="cleaning_log", 
                        names=["cleaning_log"]),                               
    ])
    unloaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name="read_me", 
                        names= ["read_me"]),
        SheetMapping(standard_name="kobo_survey", 
                        names= ["kobo_survey"]),
        SheetMapping(standard_name= "kobo_choices", 
                        names =["kobo_choices"]),        
        SheetMapping(standard_name="sampling_info", 
                        names=["sampling_info"], 
                        required=False),
        SheetMapping(standard_name="enumerator_performance_log", 
                        names=["enumerator_performance_log"], 
                        required=False)
    ])


class BaseDataset(ABC):
    @abstractmethod
    def get_schema() -> BaseDatasetSchema:
        pass

    @abstractmethod
    def get_validators() -> List[BaseValidator]:
        pass



