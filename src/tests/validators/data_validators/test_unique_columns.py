import pytest
import polars as pl

from rqa_validator.models.base import SchemaSheetMap, SchemaColumnMap
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.loaders.excel_loader import (
    DataColumnMap,
    DataSheetMap,
    ExcelLoaderData,
)
from rqa_validator.validators.data_validators.unique_column_validator import (
    UniqueColumn,
)
from rqa_validator.validators.base import BaseValidator


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return UniqueColumn(schema=valid_schema)


@pytest.fixture
def no_unique_columns_validator(no_unique_columns_schema):
    """Create a UniqueColumn validator instance"""
    return UniqueColumn(schema=no_unique_columns_schema)


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
                        standard_name="uuid",
                        alternate_names=["uuid", "X_uuid"],
                        is_unique=True,
                    )
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def no_unique_columns_schema():

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
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame(
        {
            "uuid": ["1", "1", "3", "4", "5"],
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


class TestUniqueColumns:
    def test_valid_data(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_no_unique_columns_schema(
        self,
        no_unique_columns_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = no_unique_columns_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_data(
        self, valid_schema_validator: BaseValidator, invalid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(invalid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1
