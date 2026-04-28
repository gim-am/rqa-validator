import pytest
import polars as pl

from rqa_validator.loaders.excel_loader import SheetMap, ExcelLoaderData
from rqa_validator.validators.schema_validators.unexpected_sheets_validator import UnexpectedSheets
from rqa_validator.validators.base import BaseValidator

@pytest.fixture
def valid_schema_validator():
    """Create a UniqueColumn validator instance"""
    return UnexpectedSheets()

@pytest.fixture
def unexpected_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })
    
    loaded_sheet = SheetMap(
        schema_sheet_name="raw_datax",
        data_sheet_name="raw_datax",
        data=df,
        data_columns=["uuid"]
    )
    unexpected_sheets = ['somesheet', 'anothersheet']

    data = ExcelLoaderData(loaded_sheets=[loaded_sheet]
                          )
    data.unexpected_sheets = unexpected_sheets
    
    return data

@pytest.fixture
def expected_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })
    
    loaded_sheet = SheetMap(
        schema_sheet_name="raw_datax",
        data_sheet_name="raw_datax",
        data=df,
        data_columns=["uuid"]
    )
    unexpected_sheets = []

    data = ExcelLoaderData(loaded_sheets=[loaded_sheet]
                          )
    data.unexpected_sheets = unexpected_sheets
    
    return data

class TestUnexpectedSheets:
    def test_unexpected_data(self, valid_schema_validator: BaseValidator,
                           unexpected_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(unexpected_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 2

    def test_expected_data(self, valid_schema_validator: BaseValidator,
                           expected_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(expected_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 0