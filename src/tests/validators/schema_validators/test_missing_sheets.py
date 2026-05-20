import polars as pl
import pytest

from rqa_validator.loaders.excel_loader import DataSheetMap, ExcelLoaderData
from rqa_validator.models.base import SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.schema_validators.missing_sheets_validator import (
    MissingSheetsCheck,
)
from tests.helpers import do_basic_checks


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return MissingSheetsCheck(schema=valid_schema)


@pytest.fixture
def valid_optional_schema_validator(valid_optional_schema):
    """Create a UniqueColumn validator instance"""
    return MissingSheetsCheck(schema=valid_optional_schema)


@pytest.fixture
def valid_optional_missing_schema_validator(valid_optional_missing_schema):
    """Create a UniqueColumn validator instance"""
    return MissingSheetsCheck(schema=valid_optional_missing_schema)


@pytest.fixture
def valid_optional_sampling_schema_validator(valid_optional_sampling_schema):
    """Create a UniqueColumn validator instance"""
    return MissingSheetsCheck(schema=valid_optional_sampling_schema)


@pytest.fixture
def valid_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"])
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_optional_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                required=False,
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"])
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_optional_missing_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_datax",
                alternate_names=["raw_datax"],
                required=False,
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"])
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_optional_sampling_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="sampling_info",
                alternate_names=["sampling_info"],
                required=False,
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"])
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
    )

    return ExcelLoaderData(loaded_sheets=[loaded_sheet])


@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )

    loaded_sheet = DataSheetMap(
        schema_sheet_name="raw_datax",
        data_sheet_name="raw_datax",
        data=df,
        data_columns=["uuid"],
    )

    return ExcelLoaderData(loaded_sheets=[loaded_sheet])


class TestMissingSheets:
    def test_valid_schema(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 0)

    def test_missing_sheet(
        self, valid_schema_validator: BaseValidator, invalid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(invalid_excel_data)

        do_basic_checks(result, 1)

    def test_optional_sheet(
        self,
        valid_optional_schema_validator: BaseValidator,
        invalid_excel_data: ExcelLoaderData,
    ):
        result = valid_optional_schema_validator.validate(invalid_excel_data)

        do_basic_checks(result, 1)

    def test_optional_missing_sheet(
        self,
        valid_optional_missing_schema_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = valid_optional_missing_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 1)

    def test_optional_missing_sampling_sheet(
        self,
        valid_optional_sampling_schema_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = valid_optional_sampling_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 1)
