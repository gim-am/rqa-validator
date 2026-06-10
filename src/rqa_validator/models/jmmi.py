from dataclasses import dataclass

from ..models.base_dataset import BaseDataset
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
from .default_dataset_schema import DefaultDatasetSchema


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
    def __init__(self) -> None:
        self.schema = self.get_schema()
        self.validators = self.get_validators(self.schema)

    def get_schema(self, *args, **kwargs):
        schema = JMMIDatasetSchema()
        self.lower_schema(schema)
        return schema

    def get_validators(self, *args, **kwargs) -> list[BaseValidator]:
        return [
            MissingSheetsCheck(schema=self.schema),
            UnexpectedSheetsCheck(),
            DuplicateSheetMatches(),
            MandatoryColumns(schema=self.schema),
            UniqueColumn(schema=self.schema),
            PiiDataCheck(schema=self.schema),
            CrossSheetRowSumCheck(schema=self.schema),
            CrossSheetIdCheck(schema=self.schema),
            CrossSheetIdCheck(
                schema=self.schema, master_sheet="clean_data", child_sheets=["cleaning_log"]
            ),
            CleaningLogToClean(schema=self.schema),
            RawToCleanToLog(schema=self.schema),
            NaNDataCheck(schema=self.schema),
            ConsentCheck(schema=self.schema),
            ColumnNameCheck(),
            DataTypeCheck(schema=self.schema),
            SurveyChoicesCheck(schema=self.schema),
        ]

    def process_data(self):
        return super().process_data()
