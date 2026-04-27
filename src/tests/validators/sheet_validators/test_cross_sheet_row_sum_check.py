import pytest
import polars as pl

from rqa_validator.loaders.excel_loader import SheetMap, ExcelLoaderData
from rqa_validator.validators.data_validators.cross_sheet_row_sum_check_validator import CrossSheetRowSumCheck
from rqa_validator.validators.base import BaseValidator

@pytest.fixture
def valid_schema_validator():
    """Create a UniqueColumn validator instance"""
    return CrossSheetRowSumCheck()


@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [2, 3, 4, 5],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="raw_data",
                        data_sheet_name="raw_data",
                        data=df_raw,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="deletion_log",
                        data_sheet_name="deletion_log",
                        data=df_deleted,
                        data_columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_deleted_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_deleted = pl.DataFrame({
        "uuid": [],
    })

    df_clean = pl.DataFrame({
        "uuid": [2, 3, 4, 5],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="raw_data",
                        data_sheet_name="raw_data",
                        data=df_raw,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="deletion_log",
                        data_sheet_name="deletion_log",
                        data=df_deleted,
                        data_columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_clean_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [ 3, 4, 5],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="raw_data",
                        data_sheet_name="raw_data",
                        data=df_raw,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="deletion_log",
                        data_sheet_name="deletion_log",
                        data=df_deleted,
                        data_columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_sheet_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [ 3, 4, 5],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="bla",
                        data_sheet_name="bla",
                        data=df_raw,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="blo",
                        data_sheet_name="blo",
                        data=df_clean,
                        data_columns=["uuid"]),
                        SheetMap(
                        schema_sheet_name="ble",
                        data_sheet_name="ble",
                        data=df_deleted,
                        data_columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestCrossSheetRowSum:
    def test_valid_data(self, valid_schema_validator: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_missing_deleted_data(self, valid_schema_validator: BaseValidator,
                           missing_deleted_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_deleted_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_clean_data(self, valid_schema_validator: BaseValidator,
                           missing_clean_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_clean_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_sheet_data(self, valid_schema_validator: BaseValidator,
                           missing_sheet_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_sheet_data)
        
        assert isinstance(result, list)
        assert len(result) == 3