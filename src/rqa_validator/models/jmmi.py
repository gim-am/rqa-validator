from ..models.schema import BaseDatasetSchema, BaseDataset, DefaultDatasetSchema
from ..validators.sheet_validators import UnexpectedSheets, MissingSheets

class JMMIDatasetSchema(BaseDataset):

    @staticmethod
    def get_schema() -> BaseDatasetSchema:
        schema = DefaultDatasetSchema
        schema.dataset_type = "JMMI"
        return schema
    
    @staticmethod
    def get_validators(schema: BaseDatasetSchema):                
        return[
            MissingSheets(schema=schema)
            , UnexpectedSheets()
        ]