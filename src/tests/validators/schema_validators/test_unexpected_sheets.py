import polars as pl
import pytest

from rqa_validator.loaders.excel_loader import DataSheetMap, ExcelLoaderData
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.schema_validators.unexpected_sheets_validator import (
    UnexpectedSheetsCheck,
)
from tests.helpers import do_basic_checks


@pytest.fixture
def valid_schema_validator():
    """Create a UniqueColumn validator instance"""
    return UnexpectedSheetsCheck()


@pytest.fixture
def unexpected_excel_data():
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
    unexpected_sheets = ["somesheet", "anothersheet"]

    data = ExcelLoaderData(loaded_sheets=[loaded_sheet])
    data.unexpected_sheets = unexpected_sheets

    return data

@pytest.fixture
def hidden_excel_data():
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
    hidden_excel_data = ["somesheet", "anothersheet"]

    data = ExcelLoaderData(loaded_sheets=[loaded_sheet])
    data.hidden_sheets = hidden_excel_data

    return data


@pytest.fixture
def expected_excel_data():
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
    unexpected_sheets = []

    data = ExcelLoaderData(loaded_sheets=[loaded_sheet])
    data.unexpected_sheets = unexpected_sheets

    return data


class TestUnexpectedSheets:
    def test_unexpected_data(
        self,
        valid_schema_validator: BaseValidator,
        unexpected_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(unexpected_excel_data)

        do_basic_checks(result, 1)

    def test_hidden_data(
        self,
        valid_schema_validator: BaseValidator,
        hidden_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(hidden_excel_data)

        do_basic_checks(result, 1)

    def test_expected_data(
        self,
        valid_schema_validator: BaseValidator,
        expected_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(expected_excel_data)

        do_basic_checks(result, 0)
