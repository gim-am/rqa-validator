from ..models.schema import BaseDatasetSchema, BaseDataset, DefaultDatasetSchema
from ..validators.sheet_validators import UnexpectedSheets, MissingSheets
from ..validators.column_validators import  PiiColumns, MandatoryColumns, UniqueColumn

class JMMIDatasetSchema(BaseDataset):

    @staticmethod
    def get_schema() -> DefaultDatasetSchema:
        schema = DefaultDatasetSchema(dataset_type = "JMMI")
        return schema 
    
    @staticmethod
    def get_validators(schema: BaseDatasetSchema):                
        return[
            MissingSheets(schema=schema)
            , UnexpectedSheets()
            , MandatoryColumns(schema=schema)
            , UniqueColumn(schema=schema)
            , PiiColumns()
        ]