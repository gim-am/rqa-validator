from dataclasses import dataclass, field

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
from .base import SchemaSheetMap
from .base_dataset_schemas import BaseDatasetSchema
from .defaults import (
    CHOICES_SHEET,
    CLEAN_DATA_SHEET,
    DELETION_SHEET,
    ENUMERATOR_PERFORMANCE_SHEET,
    RAW_DATA_SHEET,
    READ_ME_SHEET,
    SAMPLING_INFO_SHEET,
    SURVEY_SHEET,
    VARIABLE_TRACKER_SHEET,
    create_base_cleaning_log_sheet,
)


@dataclass()
class JMMIDatasetSchema(BaseDatasetSchema):
    dataset_type = "JMMI"

    schema_loaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            RAW_DATA_SHEET,
            CLEAN_DATA_SHEET,
            create_base_cleaning_log_sheet("cleaning_log", "uuid", ["_uuid"]),
            SURVEY_SHEET,
            CHOICES_SHEET,
            DELETION_SHEET,
        ]
    )

    schema_unloaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            READ_ME_SHEET,
            SAMPLING_INFO_SHEET,
            VARIABLE_TRACKER_SHEET,
            ENUMERATOR_PERFORMANCE_SHEET,
            SchemaSheetMap(standard_name="meb_analysis", alternate_names=["meb"]),
            SchemaSheetMap(standard_name="mfs_analysis", alternate_names=["mfs"]),
        ]
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
