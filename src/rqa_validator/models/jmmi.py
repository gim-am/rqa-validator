from .base import BaseDatasetSchema, BaseDataset, DefaultDatasetSchema
from ..validators.sheet_validators import CrossSheetRowSumCheck,UnexpectedSheets, MissingSheets, CrossSheetIdCheck
from ..validators.column_validators import  PiiColumns, MandatoryColumns, UniqueColumn
from ..validators.base import BaseValidator

from typing import List

# schema and validation rules for jmmi dataset. 
class JMMIDatasetSchema(BaseDataset):

    @staticmethod
    def get_schema(*args, **kwargs) -> DefaultDatasetSchema:
        schema = DefaultDatasetSchema(dataset_type = "JMMI")
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
        ]