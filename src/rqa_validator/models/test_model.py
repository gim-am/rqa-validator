from dataclasses import dataclass, field

from ..validators.cleaning_log_validator import CleaningLog

from .base import ProcessValueMap, SheetMapping, ColumnMapping
from ..models.base_dataset import BaseDatasetSchema, BaseDataset, DefaultDatasetSchema

from ..validators.sheet_validators import CrossSheetRowSumCheck, DuplicateSheetMatches,UnexpectedSheets, MissingSheets, CrossSheetIdCheck
from ..validators.column_validators import  ColumnNameCheck, PiiColumns, MandatoryColumns, UniqueColumn
from ..validators.data_validators import NaNCheck, ConsentCheck
from ..validators.base import BaseValidator

from typing import List


@dataclass()
class TestModelDatasetSchema(DefaultDatasetSchema):
    dataset_type = "TestModel"
    schema_loaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"],
                                                           is_unique=True),
                                            ]),
        SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns = [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"],
                                                           is_unique=True),                                             
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
                                                                                          values=['yes', 'change_response', 'blank_response'])]),
                                            ColumnMapping(standard_name="question")]),                               
    ])
    schema_unloaded_sheets: List[SheetMapping] = field(default_factory=lambda:[
        SheetMapping(standard_name="read_me", 
                        alternate_names= ["read_me"]),
        SheetMapping(standard_name="kobo_survey", 
                        alternate_names= ["survey"]),
        SheetMapping(standard_name= "kobo_choices", 
                        alternate_names =["choices"]),        
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
class TestModelDataset(BaseDataset):

    @staticmethod
    def get_schema(*args, **kwargs) -> TestModelDatasetSchema:
        schema = TestModelDatasetSchema()
        return schema 
    
    @staticmethod
    def get_validators(schema: BaseDatasetSchema, *args, **kwargs) -> List[BaseValidator]:               
        return[
            MissingSheets(schema=schema)
            , UnexpectedSheets()
            , DuplicateSheetMatches()
            , MandatoryColumns(schema=schema)
            , UniqueColumn(schema=schema)
            , PiiColumns()
            , CrossSheetRowSumCheck()
            , CrossSheetIdCheck(schema=schema)
            , CleaningLog(schema=schema)
            , NaNCheck(schema=schema)
            , ConsentCheck(schema=schema)
            , ColumnNameCheck()
        ]