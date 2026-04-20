import pytest
import polars as pl

from rqa_validator.loaders.excel_loader import SheetMap, ExcelLoaderData
from rqa_validator.validators.column_validators import PiiColumns
from rqa_validator.validators.base import BaseValidator


@pytest.fixture
def validator():
    """Create a UniqueColumn validator instance"""
    return PiiColumns()

@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })
    
    loaded_sheet = SheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["uuid"]
    )
    
    return ExcelLoaderData(loaded_sheets=[loaded_sheet])

@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "phone_number": [1, 2, 3, 4, 5],
    })
    
    loaded_sheet = SheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["phone_number"]
    )
    
    return ExcelLoaderData(loaded_sheets=[loaded_sheet])

@pytest.fixture
def invalid_fuzzy_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "phone_number1": [1, 2, 3, 4, 5],
    })
    
    loaded_sheet = SheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["phone_number1"]
    )
    
    return ExcelLoaderData(loaded_sheets=[loaded_sheet])

class TestPiiColumns():
    def test_valid_data(self, validator: BaseValidator,
                        valid_excel_data: ExcelLoaderData):
        result = validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_data(self, validator: BaseValidator,
                        invalid_excel_data: ExcelLoaderData):
        result = validator.validate(invalid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_fuzzy_data(self, validator: BaseValidator,
                        invalid_fuzzy_excel_data: ExcelLoaderData):
        result = validator.validate(invalid_fuzzy_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1