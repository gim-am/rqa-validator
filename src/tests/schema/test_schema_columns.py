import pytest
from rqa_validator.models.base import SchemaSheetMap, SchemaColumnMap
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.models.preprocess import validate_schema


@pytest.fixture
def valid_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid", alternate_names=["uuid", "X_uuid"]
                    )
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def invalid_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid", alternate_names=["uuid", "X_uuid"]
                    ),
                    SchemaColumnMap(
                        standard_name="uuid", alternate_names=["uuid", "X_uuid"]
                    ),
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def invalid_schema_2():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid", alternate_names=["uuid", "X_uuid"]
                    ),
                    SchemaColumnMap(standard_name="other", alternate_names=["uuid"]),
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


class TestSchemaSheets:
    def test_valid_schema(self, valid_schema: BaseDatasetSchema):
        result = validate_schema(valid_schema)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_schema(self, invalid_schema: BaseDatasetSchema):
        result = validate_schema(invalid_schema)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_schema2(self, invalid_schema_2: BaseDatasetSchema):
        result = validate_schema(invalid_schema_2)

        assert isinstance(result, list)
        assert len(result) == 1
