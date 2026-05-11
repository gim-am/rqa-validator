import polars as pl
import pytest

from rqa_validator.loaders.excel_loader import (
    DataColumnMap,
    DataSheetMap,
    ExcelLoaderData,
)
from rqa_validator.models.base import SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.schema_validators.mandatory_column_validator import (
    MandatoryColumns,
)


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return MandatoryColumns(schema=valid_schema)


@pytest.fixture
def valid_no_mandatory_columns_validator(valid_no_mandatory_columns):
    """Create a UniqueColumn validator instance"""
    return MandatoryColumns(schema=valid_no_mandatory_columns)


@pytest.fixture
def invalid_schema_missing_sheet_validator(invalid_schema_missing_sheet):
    """Create a UniqueColumn validator instance"""
    return MandatoryColumns(schema=invalid_schema_missing_sheet)


@pytest.fixture
def invalid_schema_missing_mandatory_column_validator(
    invalid_schema_missing_mandatory_column,
):
    """Create a UniqueColumn validator instance"""
    return MandatoryColumns(schema=invalid_schema_missing_mandatory_column)


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
def valid_no_mandatory_columns():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(standard_name="raw_data", alternate_names=["raw_data"])
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )

    loaded_sheet = DataSheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["uuid"],
        column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
    )

    return ExcelLoaderData(loaded_sheets=[loaded_sheet])


@pytest.fixture
def invalid_schema_missing_sheet():

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
            ),
            SchemaSheetMap(
                standard_name="clean_data",
                alternate_names=["clean_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid", alternate_names=["uuid", "X_uuid"]
                    )
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def invalid_schema_missing_mandatory_column():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuidx", alternate_names=["X_uuid"])
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


class TestMandatoryColumns:
    def test_valid_schema(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_no_mandatory_columns(
        self,
        valid_no_mandatory_columns_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = valid_no_mandatory_columns_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_missing_column(
        self,
        invalid_schema_missing_sheet_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = invalid_schema_missing_sheet_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_mandatory_column(
        self,
        invalid_schema_missing_mandatory_column_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = invalid_schema_missing_mandatory_column_validator.validate(
            valid_excel_data
        )

        assert isinstance(result, list)
        assert len(result) == 1
