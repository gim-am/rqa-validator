from dataclasses import dataclass, field

from rqa_validator.models.base import SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset_schemas import BaseDatasetSchema
from rqa_validator.models.defaults import (
    CHOICES_SHEET,
    CONSENT_COLUMN,
    DELETION_SHEET,
    ENUMERATOR_PERFORMANCE_SHEET,
    READ_ME_SHEET,
    SAMPLING_INFO_SHEET,
    SURVEY_SHEET,
    VARIABLE_TRACKER_SHEET,
    create_base_cleaning_log_sheet,
)


@dataclass
class DefaultDatasetSchema(BaseDatasetSchema):
    schema_loaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["_uuid"],
                        is_unique=True,
                    ),
                    CONSENT_COLUMN,
                ],
            ),
            SchemaSheetMap(
                standard_name="clean_data",
                alternate_names=["clean_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["_uuid"],
                        is_unique=True,
                    ),
                    #  SchemaColumnMap(standard_name="pop_group",
                    #                alternate_names=["pop_group"]),
                    #  SchemaColumnMap(standard_name="weight",
                    #                alternate_names=["weight"]),
                    #  SchemaColumnMap(standard_name="person_id",
                    #                alternate_names=["person_id"])
                ],
            ),
            DELETION_SHEET,
            create_base_cleaning_log_sheet("cleaning_log", "uuid", ["_uuid"]),
            SURVEY_SHEET,
            CHOICES_SHEET,
        ]
    )
    schema_unloaded_sheets: list[SchemaSheetMap] = field(
        default_factory=lambda: [
            READ_ME_SHEET,
            SAMPLING_INFO_SHEET,
            VARIABLE_TRACKER_SHEET,
            ENUMERATOR_PERFORMANCE_SHEET,
        ]
    )
