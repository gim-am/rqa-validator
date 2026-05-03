
import pytest
import polars as pl


from rqa_validator.loaders.excel_loader import DataSheetMap, ExcelLoaderData
from rqa_validator.validators.schema_validators.column_name_validator import ColumnNameCheck
from rqa_validator.validators.base import BaseValidator


@pytest.fixture
def validator():
    """Create a UniqueColumn validator instance"""
    return ColumnNameCheck()


@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "some_column": [1, 2, 3, 4, 5],
        "some.column": [1, 2, 3, 4, 5],
        "SomeColumn": [1, 2, 3, 4, 5]
    })
    
    loaded_sheet = DataSheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["uuid", 'some_column', "some.column", "SomeColumn"]
    )
    
    return ExcelLoaderData(loaded_sheets=[loaded_sheet])

@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "some column": [1, 2, 3, 4, 5]
    })
    
    loaded_sheet = DataSheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["uuid", 'some column']
    )
    
    return ExcelLoaderData(loaded_sheets=[loaded_sheet])

@pytest.fixture
def invalid_excel_data2():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "some@column": [1, 2, 3, 4, 5]
    })
    
    loaded_sheet = DataSheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["uuid", 'some column']
    )
    
    return ExcelLoaderData(loaded_sheets=[loaded_sheet])

class TestColumnNames():
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

    def test_invalid_data2(self, validator: BaseValidator,
                        invalid_excel_data2: ExcelLoaderData):
        result = validator.validate(invalid_excel_data2)
        
        assert isinstance(result, list)
        assert len(result) == 1