from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SheetMapping:
    standard_name: str
    names: List[str]  
    required: bool = True    
    
    def matches(self, sheet_name: str) -> bool:
        return sheet_name in self.names
    
@dataclass
class ColumnMapping:
    # standard_name: str
    
    names: List[str] 
    sheet: str = None 
    


@dataclass
class BaseDatasetSchema:
    dataset_type: str = None
    # sheets that have to be loaded and used for further validation
    loaded_sheets: List[SheetMapping]= None
    # sheets that should exist but dont need to be loaded
    unloaded_sheets: List[SheetMapping]   = None 

    mandatory_columns: List[ColumnMapping]= None

    # removeable_columns: Dict[str, List[ColumnMapping]] 


@dataclass
class DefaultDatasetSchema(BaseDatasetSchema):
    loaded_sheets=[
        SheetMapping(standard_name= "raw_data", 
                        names =["raw_data"]),
        SheetMapping(standard_name= "variable_tracker", 
                        names =["variable_tracker"]),
        SheetMapping(standard_name= "clean_data", 
                        names =["clean_data"]),
        SheetMapping(standard_name= "deletion_log", 
                        names =["deletion_log"]),                                
    ],
    unloaded_sheets=[
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
                        required=False),
    ],

    mandatory_columns = [
        ColumnMapping(sheet="clean_data",
                        names=["uuid","stratum","pop_group","weight","person_id"])
    ]

class BaseDataset(ABC):
    @abstractmethod
    def get_schema() -> BaseDatasetSchema:
        pass

    @abstractmethod
    def get_validators() -> List:
        pass



