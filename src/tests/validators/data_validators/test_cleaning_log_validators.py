import pytest
import polars as pl

from rqa_validator.models.base import ProcessValueMap, SheetMapping, ColumnMapping
from rqa_validator.loaders.excel_loader import ColumnMap, SheetMap, ExcelLoaderData
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.data_validators import CleaningLog
from rqa_validator.validators.base import BaseValidator

@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return CleaningLog(schema=valid_schema)

@pytest.fixture
def invalid_schema_validator(invalid_schema):
    """Create a UniqueColumn validator instance"""
    return CleaningLog(schema=invalid_schema)

@pytest.fixture
def valid_schema():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "clean_data", 
                        alternate_names =["clean_data"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuidx", "X_uuid"],
                                                           is_unique=True)],  
                        )
                        ,SheetMapping(standard_name= "cleaning_log", 
                        alternate_names =["cleaning_log"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"]
                                                           ),
                                            ColumnMapping(standard_name="new_value"),
                                            ColumnMapping(standard_name="question"),
                                            ColumnMapping(standard_name="change_type",
                                                          alternate_names=["changed"],
                                                          process_values=[ProcessValueMap(process_name='cleaning_log_validation',
                                                                                          values=['yes', 'change_response'])])],  
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
                                                           is_unique=True)],  
                        )
                        ,SheetMapping(standard_name= "cleaning_log", 
                        alternate_names =["cleaning_log"],
                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                           alternate_names=["uuid", "X_uuid"]
                                                           ),
                                            ColumnMapping(standard_name="new_value"),
                                            ColumnMapping(standard_name="question"),
                                            ColumnMapping(standard_name="change_type")],  
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

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_clean_data_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 7],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_cleanlog_data_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[7],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_question_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question6": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question6", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_question_log_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question6'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_sheet_1_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_datamis",
                        data_sheet_name="clean_datamis",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_sheet_2_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_logmiss",
                        data_sheet_name="cleaning_logmiss",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)



@pytest.fixture
def missing_column_1_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuidmiss": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuidmiss", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuidmiss',
                                   data_column_name='uuidmiss')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_2_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuidmiss": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuidmiss", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuidmiss',
                                   data_column_name='uuidmiss'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_3_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_valuemiss":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_valuemiss", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_valuemiss',
                                   data_column_name='new_valuemiss'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_column_4_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "questionmiss":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "questionmiss", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'questionmiss',
                                   data_column_name='questionmiss'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def multi_entry_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5, 5],
        "question":['question1', 'question1'],
        "new_value":[5, 6],
        "change_type": ["change_response", "change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type'),
                                   ])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def valid_excel_data_empty_value():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [1],
        "question":['question2'],
        "new_value":[''],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data_empty_value():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [1],
        "question":['question2'],
        "new_value":[''],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question'),
                                   ColumnMap(schema_column_name = 'change_type',
                                   data_column_name='change_type')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_change_type():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "question1": [1, 2, 3, 4, 5],
        "question2":["a", "c", "f", "a", "a"]
    })

    df_clean_log = pl.DataFrame({
        "uuid": [5],
        "question":['question1'],
        "new_value":[5],
        "change_type": ["change_response"]
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="cleaning_log",
                        data_sheet_name="cleaning_log",
                        data=df_clean_log,
                        data_columns=["uuid", "question", "new_value", "change_type"],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid'),
                                   ColumnMap(schema_column_name = 'new_value',
                                   data_column_name='new_value'),
                                   ColumnMap(schema_column_name = 'question',
                                   data_column_name='question')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

class TestCleaningLog:
    def test_valid_data(self, valid_schema_validator: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_cleanlog_data(self, valid_schema_validator: BaseValidator,
                           invalid_cleanlog_data_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_cleanlog_data_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_clean_data(self, valid_schema_validator: BaseValidator,
                           invalid_clean_data_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_clean_data_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_question_clean_data(self, valid_schema_validator: BaseValidator,
                           missing_question_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_question_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_question_log_data(self, valid_schema_validator: BaseValidator,
                           missing_question_log_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_question_log_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_sheet_1_data(self, valid_schema_validator: BaseValidator,
                           missing_sheet_1_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_sheet_1_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_sheet_2_data(self, valid_schema_validator: BaseValidator,
                           missing_sheet_2_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_sheet_2_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column_1_data(self, valid_schema_validator: BaseValidator,
                           missing_column_1_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_column_1_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column_2_data(self, valid_schema_validator: BaseValidator,
                           missing_column_2_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_column_2_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column_3_data(self, valid_schema_validator: BaseValidator,
                           missing_column_3_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_column_3_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column_4_data(self, valid_schema_validator: BaseValidator,
                           missing_column_4_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_column_4_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_multientry_data(self, valid_schema_validator: BaseValidator,
                           multi_entry_data: ExcelLoaderData):
        result = valid_schema_validator.validate(multi_entry_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_empty_value_data(self, valid_schema_validator: BaseValidator,
                           valid_excel_data_empty_value: ExcelLoaderData):
        result = valid_schema_validator.validate(valid_excel_data_empty_value)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_empty_value_data_invalid(self, valid_schema_validator: BaseValidator,
                           invalid_excel_data_empty_value: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_excel_data_empty_value)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_change_type_column(self, valid_schema_validator: BaseValidator,
                           missing_change_type: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_change_type)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_schema(self, invalid_schema_validator: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = invalid_schema_validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        #  missing columns, multiple edits