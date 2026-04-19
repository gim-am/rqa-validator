from dataclasses import dataclass, field

from .base import SheetMapping, ColumnMapping
from ..models.base_dataset import BaseDatasetSchema, BaseDataset, DefaultDatasetSchema

from ..validators.sheet_validators import CrossSheetRowSumCheck,UnexpectedSheets, MissingSheets, CrossSheetIdCheck
from ..validators.column_validators import  PiiColumns, MandatoryColumns, UniqueColumn
from ..validators.data_validators import CleaningLog
from ..validators.base import BaseValidator

from typing import List


@dataclass()
class JMMIDatasetSchema(DefaultDatasetSchema):
    dataset_type = "JMMI"
    # def __post_init__(self):
    #     self.schema_loaded_sheets.append


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