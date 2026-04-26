from dataclasses import dataclass

from ..validators.cleaning_log_validator import CleaningLog

from .base import SheetMapping, ColumnMapping
from ..models.base_dataset import BaseDatasetSchema, BaseDataset, DefaultDatasetSchema

from ..validators.sheet_validators import CrossSheetRowSumCheck, DuplicateSheetMatches,UnexpectedSheets, MissingSheets, CrossSheetIdCheck
from ..validators.column_validators import  ColumnNameCheck, PiiColumns, MandatoryColumns, UniqueColumn
from ..validators.data_validators import NaNCheck, ConsentCheck
from ..validators.base import BaseValidator

from typing import List


@dataclass()
class JMMIDatasetSchema(DefaultDatasetSchema):
    dataset_type = "JMMI"
    def __post_init__(self):
        self.add_unloaded_sheet(SheetMapping(standard_name="meb_analysis", 
                                                    alternate_names= ["meb"]))
        self.add_unloaded_sheet(SheetMapping(standard_name="mfs_analysis", 
                                                    alternate_names= ["mfs"]))
        self.add_mandatory_column_to_sheet('clean_data',
                                           ColumnMapping(standard_name="stratum",
                                                           alternate_names=["stratum"]))



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