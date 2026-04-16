from dataclasses import dataclass, field

from .base import SheetMapping, ColumnMapping
from ..models.base_dataset import BaseDatasetSchema, BaseDataset

from ..validators.sheet_validators import CrossSheetRowSumCheck,UnexpectedSheets, MissingSheets, CrossSheetIdCheck
from ..validators.column_validators import  PiiColumns, MandatoryColumns, UniqueColumn
from ..validators.data_validators import CleaningLog
from ..validators.base import BaseValidator

from typing import List


@dataclass()
class JMMIDatasetSchema(BaseDatasetSchema):
    dataset_type = "JMMI"
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


# schema and validation rules for jmmi dataset. 
class JMMIDataset(BaseDataset):

    @staticmethod
    def get_schema(*args, **kwargs) -> JMMIDatasetSchema:
        schema = JMMIDatasetSchema()
        return schema 
    
    @staticmethod
    def get_validators(schema: BaseDatasetSchema, *args, **kwargs) -> List[BaseValidator]:               
        return[
            MissingSheets(schema=schema)
            , UnexpectedSheets()
            , MandatoryColumns(schema=schema)
            , UniqueColumn(schema=schema)
            , PiiColumns()
            , CrossSheetRowSumCheck()
            , CrossSheetIdCheck(schema=schema)
            , CleaningLog(schema=schema)
        ]