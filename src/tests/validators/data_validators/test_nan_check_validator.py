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
from rqa_validator.validators.data_validators.nan_check_validator import NaNDataCheck
from tests.helpers import do_basic_checks, error_counter


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return NaNDataCheck(schema=valid_schema)


@pytest.fixture
def invalid_schema_validator(invalid_schema):
    """Create a UniqueColumn validator instance"""
    return NaNDataCheck(schema=invalid_schema)


@pytest.fixture
def valid_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="clean_data",
                alternate_names=["clean_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuidx", "X_uuid", "uuid2"],
                        is_unique=True,
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
                standard_name="clean_data",
                alternate_names=["clean_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuidx", "X_uuid"],
                        is_unique=True,
                    ),
                    SchemaColumnMap(
                        standard_name="uuid2", alternate_names=["uuid2"], is_unique=True
                    ),
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": ["1", "2", "3", "4", "5"],
            "question1": [-999, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data2():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": ["1", "2", "3", "4", "5"],
            "question1": [-999, 2, 3, 4, 5],
            "question2": ["a", "999", "f", "a", "a"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data3():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": ["1", "2", "3", "4", "5"],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "b", "f", "a", "a"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_dataxxx",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data4():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": ["1", "2", "3", "4", "5"],
            "uuid2": ["1", "2", "3", "4", "5"],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "b", "f", "a", "a"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "uuid2", "question1", "question2"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="uuid2", data_column_name="uuid2"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestCleaningLog:
    def test_valid_data(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 0)

    def test_invalid_data(
        self, valid_schema_validator: BaseValidator, invalid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(invalid_excel_data)

        filtered_results = error_counter(result)
        do_basic_checks(filtered_results, 1)
        assert filtered_results[0].details is not None
        assert len(filtered_results[0].details["uuid"]) == 1

    def test_invalid_data2(
        self,
        valid_schema_validator: BaseValidator,
        invalid_excel_data2: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_excel_data2)

        filtered_results = error_counter(result)
        do_basic_checks(filtered_results, 1)
        assert filtered_results[0].details is not None
        assert len(filtered_results[0].details["uuid"]) == 2

    def test_invalid_data3(
        self,
        valid_schema_validator: BaseValidator,
        invalid_excel_data3: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_excel_data3)

        do_basic_checks(result, 1)

    def test_invalid_data4(
        self,
        invalid_schema_validator: BaseValidator,
        invalid_excel_data4: ExcelLoaderData,
    ):
        result = invalid_schema_validator.validate(invalid_excel_data4)

        do_basic_checks(result, 1)
