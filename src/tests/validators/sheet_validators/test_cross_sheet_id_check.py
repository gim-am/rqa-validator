import pytest
import polars as pl

from rqa_validator.models.schema import SheetMapping, ColumnMapping, BaseDatasetSchema
from rqa_validator.loaders.excel_loader import LoadedSheet, ExcelLoaderData
from rqa_validator.validators.sheet_validators import CrossSheetIdCheck
from rqa_validator.validators.base import BaseValidator

@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return CrossSheetIdCheck(schema=valid_schema)


@pytest.fixture
def valid_schema():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"])],  
                        unique_columns = ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid"]),
                                            )
                        ,SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid"])],  
                        unique_columns = ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid"]))
                        ,SheetMapping(standard_name= "deletion_log", 
                        alternate_names =["deletion_log"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"])],  
                        unique_columns = ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"]))
                        ,SheetMapping(standard_name= "cleaning_log", 
                        alternate_names =["cleaning_log"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"])],  
                        unique_columns = ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"]))                                   
                                                           ],
        schema_unloaded_sheets=[]
    )



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

    df_clean_log = pl.DataFrame({
        "uuid": [ 5],
    })
    
    loaded_sheets = [LoadedSheet(
                        mapped_name="raw_data",
                        original_name="raw_data",
                        data=df_raw,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="clean_data",
                        original_name="clean_data",
                        data=df_clean,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="deletion_log",
                        original_name="deletion_log",
                        data=df_deleted,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="cleaning_log",
                        original_name="cleaning_log",
                        data=df_clean_log,
                        columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def master_extra_id_column_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "uuidx": [1, 2, 3, 4, 5]
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [2, 3, 4, 5],
    })

    df_clean_log = pl.DataFrame({
        "uuid": [ 5],
    })
    
    loaded_sheets = [LoadedSheet(
                        mapped_name="raw_data",
                        original_name="raw_data",
                        data=df_raw,
                        columns=["uuid", "uuidx"]),
                        LoadedSheet(
                        mapped_name="clean_data",
                        original_name="clean_data",
                        data=df_clean,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="deletion_log",
                        original_name="deletion_log",
                        data=df_deleted,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="cleaning_log",
                        original_name="cleaning_log",
                        data=df_clean_log,
                        columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_extra_id_column_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5]        
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [2, 3, 4, 5],
        "uuidx": [2, 3, 4, 5]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [ 5],
    })
    
    loaded_sheets = [LoadedSheet(
                        mapped_name="raw_data",
                        original_name="raw_data",
                        data=df_raw,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="clean_data",
                        original_name="clean_data",
                        data=df_clean,
                        columns=["uuid","uuidx"]),
                        LoadedSheet(
                        mapped_name="deletion_log",
                        original_name="deletion_log",
                        data=df_deleted,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="cleaning_log",
                        original_name="cleaning_log",
                        data=df_clean_log,
                        columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_missing_id_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5]        
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [2, 3, 4, 5, 7],
    })

    df_clean_log = pl.DataFrame({
        "uuid": [ 5],
    })
    
    loaded_sheets = [LoadedSheet(
                        mapped_name="raw_data",
                        original_name="raw_data",
                        data=df_raw,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="clean_data",
                        original_name="clean_data",
                        data=df_clean,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="deletion_log",
                        original_name="deletion_log",
                        data=df_deleted,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="cleaning_log",
                        original_name="cleaning_log",
                        data=df_clean_log,
                        columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_missing_sheets_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5]        
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [2, 3, 4, 5, 7],
    })

    df_clean_log = pl.DataFrame({
        "uuid": [ 5],
    })
    
    loaded_sheets = [LoadedSheet(
                        mapped_name="raw_data",
                        original_name="raw_data",
                        data=df_raw,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="clean_datax",
                        original_name="clean_datax",
                        data=df_clean,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="deletion_logx",
                        original_name="deletion_logx",
                        data=df_deleted,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="cleaning_logx",
                        original_name="cleaning_logx",
                        data=df_clean_log,
                        columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def master_missing_sheets_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5]        
    })

    df_deleted = pl.DataFrame({
        "uuid": [1],
    })

    df_clean = pl.DataFrame({
        "uuid": [2, 3, 4, 5, 7],
    })

    df_clean_log = pl.DataFrame({
        "uuid": [ 5],
    })
    
    loaded_sheets = [LoadedSheet(
                        mapped_name="raw_datax",
                        original_name="raw_datax",
                        data=df_raw,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="clean_data",
                        original_name="clean_data",
                        data=df_clean,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="deletion_log",
                        original_name="deletion_log",
                        data=df_deleted,
                        columns=["uuid"]),
                        LoadedSheet(
                        mapped_name="cleaning_log",
                        original_name="cleaning_log",
                        data=df_clean_log,
                        columns=["uuid"])]

    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestCrossSheetIdCheck:
    def test_valid_data(self, valid_schema_validator: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_master_extra_id_column_data(self, valid_schema_validator: BaseValidator,
                           master_extra_id_column_data: ExcelLoaderData):
        result = valid_schema_validator.validate(master_extra_id_column_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_child_extra_id_column_data(self, valid_schema_validator: BaseValidator,
                           child_extra_id_column_data: ExcelLoaderData):
        result = valid_schema_validator.validate(child_extra_id_column_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_child_extra_id_data(self, valid_schema_validator: BaseValidator,
                           child_missing_id_data: ExcelLoaderData):
        result = valid_schema_validator.validate(child_missing_id_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_child_missing_sheets_data(self, valid_schema_validator: BaseValidator,
                           child_missing_sheets_data: ExcelLoaderData):
        result = valid_schema_validator.validate(child_missing_sheets_data)
        
        assert isinstance(result, list)
        assert len(result) == 3

    def test_master_missing_sheets_data(self, valid_schema_validator: BaseValidator,
                           master_missing_sheets_data: ExcelLoaderData):
        result = valid_schema_validator.validate(master_missing_sheets_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

