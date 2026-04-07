from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ColumnMapping:
    standard_name: str    
    names: List[str] 

    def combine(self):
        if self.standard_name not in self.names:
            return self.names.append(self.standard_name)
        else:
            return self.names

@dataclass
class SheetMapping:
    standard_name: str
    names: List[str]  
    mandatory_columns: List[ColumnMapping] = field(default_factory=list)
    required: bool = True  
    unique_uuid: bool = False
    unique_uuid_column: Optional[ColumnMapping] = field(default_factory=lambda: ColumnMapping(None, []))
     
    def matches(self, sheet_name: str) -> bool:
        return sheet_name in self.names    


@dataclass
class BaseDatasetSchema:
    dataset_type: str 
    # sheets that have to be loaded and used for further validation
    loaded_sheets: List[SheetMapping]= field(default_factory=list)
    # sheets that should exist but dont need to be loaded
    unloaded_sheets: List[SheetMapping]   = field(default_factory=list) 


@dataclass()
class DefaultDatasetSchema(BaseDatasetSchema):

    loaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name= "raw_data", 
                        names =["raw_data"],
                        unique_uuid=True,
                        unique_uuid_column= ColumnMapping(standard_name="uuid",
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
                        unique_uuid=True,
                        unique_uuid_column= ColumnMapping(standard_name="uuid",
                                                           names=["uuid", "X_uuid"])),
        SheetMapping(standard_name= "deletion_log", 
                        names =["deletion_log"])                                
    ])
    unloaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name="read_me", 
                        names= ["read_me"]),
        SheetMapping(standard_name="kobo_survey", 
                        names= ["kobo_survey"]),
        SheetMapping(standard_name= "kobo_choices", 
                        names =["kobo_choices"]),
        SheetMapping(standard_name="cleaning_log", 
                        names=["cleaning_log"]),
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
    def get_validators() -> List:
        pass



