from dataclasses import dataclass

from ..validators.data_validators.survey_choices_validator import SurveyChoicesCheck

from ..validators.data_validators.column_data_type_validator import DataTypeCheck
from ..validators.data_validators.cross_sheet_row_sum_check_validator import CrossSheetRowSumCheck
from ..validators.schema_validators.unexpected_sheets_validator import UnexpectedSheets
from ..validators.schema_validators.missing_sheets_validator import MissingSheets
from ..validators.schema_validators.duplicate_sheet_match_validator import DuplicateSheetMatches
from ..validators.schema_validators.mandatory_column_validator import MandatoryColumns
from ..validators.data_validators.pii_validator import PiiColumns
from ..validators.data_validators.unique_column_validator import UniqueColumn
from ..validators.data_validators.consent_check_validator import ConsentCheck
from ..validators.data_validators.cleaning_log_validator import CleaningLog
from ..validators.data_validators.cross_sheet_id_check_validator import CrossSheetIdCheck
from ..validators.schema_validators.column_name_validator import  ColumnNameCheck
from ..validators.data_validators.nan_check_validator import NaNCheck
from ..validators.base import BaseValidator
from .base import SheetMapping, ColumnMapping
from ..models.base_dataset import BaseDatasetSchema, BaseDataset, DefaultDatasetSchema



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
            , DataTypeCheck(schema=schema)
            , SurveyChoicesCheck(schema=schema)
        ]