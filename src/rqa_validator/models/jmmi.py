from dataclasses import dataclass

from ..models.base_dataset import BaseDataset, BaseDatasetSchema, DefaultDatasetSchema
from ..validators.base import BaseValidator
from ..validators.data_validators import (
    CleaningLogToClean,
    ConsentCheck,
    CrossSheetIdCheck,
    CrossSheetRowSumCheck,
    DataTypeCheck,
    NaNDataCheck,
    PiiDataCheck,
    RawToCleanToLog,
    SurveyChoicesCheck,
    UniqueColumn,
)
from ..validators.schema_validators import (
    ColumnNameCheck,
    DuplicateSheetMatches,
    MandatoryColumns,
    MissingSheetsCheck,
    UnexpectedSheetsCheck,
)
from .base import SchemaColumnMap, SchemaSheetMap


@dataclass()
class JMMIDatasetSchema(DefaultDatasetSchema):
    dataset_type = "JMMI"

    def __post_init__(self):
        self.add_unloaded_sheet(
            SchemaSheetMap(standard_name="meb_analysis", alternate_names=["meb"])
        )
        self.add_unloaded_sheet(
            SchemaSheetMap(standard_name="mfs_analysis", alternate_names=["mfs"])
        )
        self.add_mandatory_column_to_sheet(
            "clean_data",
            SchemaColumnMap(standard_name="stratum", alternate_names=["stratum"]),
        )


# schema and validation rules for jmmi dataset.
class JMMIDataset(BaseDataset):
    @staticmethod
    def get_schema(*args, **kwargs) -> JMMIDatasetSchema:
        schema = JMMIDatasetSchema()
        return schema

    @staticmethod
    def get_validators(schema: BaseDatasetSchema, *args, **kwargs) -> list[BaseValidator]:
        return [
            MissingSheetsCheck(schema=schema),
            UnexpectedSheetsCheck(),
            DuplicateSheetMatches(),
            MandatoryColumns(schema=schema),
            UniqueColumn(schema=schema),
            PiiDataCheck(schema=schema),
            CrossSheetRowSumCheck(schema=schema),
            CrossSheetIdCheck(schema=schema),
            CrossSheetIdCheck(
                schema=schema, master_sheet="clean_data", child_sheets=["cleaning_log"]
            ),
            CleaningLogToClean(schema=schema),
            RawToCleanToLog(schema=schema),
            NaNDataCheck(schema=schema),
            ConsentCheck(schema=schema),
            ColumnNameCheck(),
            DataTypeCheck(schema=schema),
            SurveyChoicesCheck(schema=schema),
        ]
