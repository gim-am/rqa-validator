import pytest
import polars as pl

from rqa_validator.models.base import  ProcessValueMap, SheetMapping, ColumnMapping
from rqa_validator.loaders.excel_loader import ColumnMap, SheetMap, ExcelLoaderData
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.data_validators.consent_check_validator import ConsentCheck
from rqa_validator.validators.base import BaseValidator

@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return ConsentCheck(schema=valid_schema)

@pytest.fixture
def invalid_schema_validator(invalid_schema):
    """Create a UniqueColumn validator instance"""
    return ConsentCheck(schema=invalid_schema)

@pytest.fixture
def invalid_schema_validator2(invalid_schema2):
    """Create a UniqueColumn validator instance"""
    return ConsentCheck(schema=invalid_schema2)

@pytest.fixture
def invalid_schema_validator3(invalid_schema3):
    """Create a UniqueColumn validator instance"""
    return ConsentCheck(schema=invalid_schema3)

@pytest.fixture
def invalid_schema_validator4(invalid_schema4):
    """Create a UniqueColumn validator instance"""
    return ConsentCheck(schema=invalid_schema4)
@pytest.fixture
def valid_schema():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True)],  
                        ),
                        SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True),
                                            ColumnMapping(standard_name="consent",
                                                            alternate_names=[],
                                                            process_values=[ProcessValueMap(process_name='consent_check_validation',
                                                                                          values=['yes'])])],  
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
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True)],  
                        ),
                        SheetMapping(standard_name= "raw_dataxx", 
                        alternate_names =["raw_dataxx"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True),
                                            ColumnMapping(standard_name="consent",
                                                            alternate_names=[],
                                                            process_values=[ProcessValueMap(process_name='consent_check_validation',
                                                                                          values=['yes'])])],  
                        )
                        ],
        schema_unloaded_sheets=[]
    )

@pytest.fixture
def invalid_schema2():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True)],  
                        ),
                        SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True),
                                            ColumnMapping(standard_name="consent",
                                                            alternate_names=[],
                                                            process_values=[ProcessValueMap(process_name='consent_check_validation',
                                                                                          values=[])])],  
                        )
                        ],
        schema_unloaded_sheets=[]
    )

@pytest.fixture
def invalid_schema3():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=False)],  
                        ),
                        SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True),
                                            ColumnMapping(standard_name="consent",
                                                            alternate_names=[],
                                                            process_values=[ProcessValueMap(process_name='consent_check_validation',
                                                                                          values=['yes'])])],  
                        )
                        ],
        schema_unloaded_sheets=[]
    )

@pytest.fixture
def invalid_schema4():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=True)],  
                        ),
                        SheetMapping(standard_name= "raw_data", 
                        alternate_names =["raw_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid", "uuid2"],
                                                           is_unique=False),
                                            ColumnMapping(standard_name="consent",
                                                            alternate_names=[],
                                                            process_values=[ProcessValueMap(process_name='consent_check_validation',
                                                                                          values=['yes'])])],  
                        )
                        ],
        schema_unloaded_sheets=[]
    )

@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "consent": ['yes', 'yes', 'yes', 'yes', 'yes'],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                    SheetMap(
                        schema_sheet_name="raw_data",
                        data_sheet_name="raw_data",
                        data=df_raw,
                        data_columns=["uuid", "consent"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'consent',
                                   data_column_name='consent')])
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "consent": ['yes', 'no', 'yes', 'yes', 'no'],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                    SheetMap(
                        schema_sheet_name="raw_data",
                        data_sheet_name="raw_data",
                        data=df_raw,
                        data_columns=["uuid", "consent"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'consent',
                                   data_column_name='consent')])
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data2():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "consent": ['yes', 'yes', 'yes', 'yes', 'yes'],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_dataxx",
                        data_sheet_name="clean_dataxx",
                        data=df_clean,
                        data_columns=["uuid"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                    SheetMap(
                        schema_sheet_name="raw_data",
                        data_sheet_name="raw_data",
                        data=df_raw,
                        data_columns=["uuid", "consent"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'consent',
                                   data_column_name='consent')])
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data3():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "consent": ['yes', 'yes', 'yes', 'yes', 'yes'],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                    SheetMap(
                        schema_sheet_name="raw_dataxx",
                        data_sheet_name="raw_dataxx",
                        data=df_raw,
                        data_columns=["uuid", "consent"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'consent',
                                   data_column_name='consent')])
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data4():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
    })

    df_raw = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "consent": ['yes', 'yes', 'yes', 'yes', 'yes'],
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                    SheetMap(
                        schema_sheet_name="raw_data",
                        data_sheet_name="raw_data",
                        data=df_raw,
                        data_columns=["uuid", "consent"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')])
                        ]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

class TestConsentCheck:
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
        assert len(result[0].details['uuid']) == 2

    def test_invalid_data2(self, valid_schema_validator: BaseValidator,
                           invalid_excel_data2: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_excel_data2)
        
        assert isinstance(result, list)
        assert len(result) == 1    
    
    def test_invalid_data3(self, valid_schema_validator: BaseValidator,
                           invalid_excel_data3: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_excel_data3)
        
        assert isinstance(result, list)
        assert len(result) == 1   

    def test_invalid_data4(self, valid_schema_validator: BaseValidator,
                           invalid_excel_data4: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_excel_data4)
        
        assert isinstance(result, list)
        assert len(result) == 1  

    def test_invalid_schema(self, invalid_schema_validator: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = invalid_schema_validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1  

    def test_invalid_schema2(self, invalid_schema_validator2: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = invalid_schema_validator2.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1  

    def test_invalid_schema3(self, invalid_schema_validator3: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = invalid_schema_validator3.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1  

    def test_invalid_schema4(self, invalid_schema_validator4: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = invalid_schema_validator4.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1  