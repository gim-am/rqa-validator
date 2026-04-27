import pytest
import polars as pl

from rqa_validator.models.base import  SheetMapping, ColumnMapping
from rqa_validator.loaders.excel_loader import ColumnMap, SheetMap, ExcelLoaderData
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.data_validators.nan_check_validator import NaNCheck
from rqa_validator.validators.base import BaseValidator

@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return NaNCheck(schema=valid_schema)

@pytest.fixture
def invalid_schema_validator(invalid_schema):
    """Create a UniqueColumn validator instance"""
    return NaNCheck(schema=invalid_schema)

@pytest.fixture
def valid_schema():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True)],  
                        )
                        ],
        schema_unloaded_sheets=[]
    )

@pytest.fixture
def invalid_schema():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid"],
                                                           is_unique=True),
                                            ColumnMapping(standard_name="uuid2",
                                                           alternate_names=["uuid2"],
                                                           is_unique=True)],  
                        )
                        ],
        schema_unloaded_sheets=[]
    )

@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": ['1', '2', '3', '4', '5'],
        "question1": [-999, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data2():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": ['1', '2', '3', '4', '5'],
        "question1": [-999, 2, 3, 4, 5],
        "question2":["a", "999", "f", "a", "a"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data3():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": ['1', '2', '3', '4', '5'],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "b", "f", "a", "a"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_dataxxx",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data4():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": ['1', '2', '3', '4', '5'],
        "uuid2": ['1', '2', '3', '4', '5'],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "b", "f", "a", "a"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "uuid2", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'uuid2',
                                   data_column_name='uuid2')]),
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestCleaningLog:
    def test_valid_data(self, valid_schema_validator: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_data(self, valid_schema_validator: BaseValidator,
                           invalid_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_excel_data)
        
        assert isinstance(result, list)        
        assert len(result) == 1
        assert len(result[0].details['uuid']) == 1

    def test_invalid_data2(self, valid_schema_validator: BaseValidator,
                           invalid_excel_data2: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_excel_data2)
        
        assert isinstance(result, list)        
        assert len(result) == 1
        assert len(result[0].details['uuid']) == 2

    def test_invalid_data3(self, valid_schema_validator: BaseValidator,
                           invalid_excel_data3: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_excel_data3)
        
        assert isinstance(result, list)        
        assert len(result) == 1

    def test_invalid_data4(self, invalid_schema_validator: BaseValidator,
                           invalid_excel_data4: ExcelLoaderData):
        result = invalid_schema_validator.validate(invalid_excel_data4)
        
        assert isinstance(result, list)        
        assert len(result) == 1

