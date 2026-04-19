from typing import List

from ..models.base import ColumnMapping, SheetMapping, ProcessValueMap

from ..validators.base import BaseValidator
from abc import abstractmethod, ABC
from dataclasses import dataclass, field

@dataclass
class BaseDatasetSchema:
    dataset_type: str = str()
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

@dataclass
class DefaultDatasetSchema(BaseDatasetSchema):
    schema_loaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"],
                                                           is_unique=True)]
                                                        ),
        SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns = [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"],
                                                           is_unique=True),
                                             ColumnMapping(standard_name="stratum",
                                                           alternate_names=["stratum"]),
                                             ColumnMapping(standard_name="pop_group",
                                                           alternate_names=["pop_group"]),
                                             ColumnMapping(standard_name="weight",
                                                           alternate_names=["weight"]),
                                             ColumnMapping(standard_name="person_id",
                                                           alternate_names=["person_id"])
                                            ]),
        SheetMapping(standard_name= "deletion_log", 
                        alternate_names =["deletion_log"],                        
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                          is_unique=True),
                                             ]),
        SheetMapping(standard_name="cleaning_log", 
                        alternate_names=["clog_logbook"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid"),
                                            ColumnMapping(standard_name="old_value"),
                                            ColumnMapping(standard_name="new_value"),
                                            ColumnMapping(standard_name="change_type",
                                                          alternate_names=["changed"],
                                                          process_values=[ProcessValueMap(process_name='cleaning_log_validation',
                                                                                          values=['yes', 'change_response'])]),
                                            ColumnMapping(standard_name="question")]),                               
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
        SheetMapping(standard_name= "variable_tracker", 
                        alternate_names =["variable_tracker"]),
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