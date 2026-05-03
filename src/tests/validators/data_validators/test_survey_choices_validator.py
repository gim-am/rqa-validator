import pytest
import polars as pl

from rqa_validator.models.base import ProcessValueMap, SheetMapping, ColumnMapping
from rqa_validator.loaders.excel_loader import ColumnMap, SheetMap, ExcelLoaderData
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.data_validators.survey_choices_validator import SurveyChoicesCheck
from rqa_validator.validators.base import BaseValidator

@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return SurveyChoicesCheck(schema=valid_schema)



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
                        ,SheetMapping(standard_name="kobo_survey", 
                        alternate_names= ["survey"],
                        mandatory_columns = [ColumnMapping(standard_name='type',
                                                           process_values=[ProcessValueMap(process_name='data_type_numeric_check',
                                                                                           values = ['integer', 'decimal']),
                                                                            ProcessValueMap(process_name='data_type_temporal_check',
                                                                                           values = ['date'])]),
                                             ColumnMapping(standard_name= 'name')]),  
                                             
                        SheetMapping(standard_name= "kobo_choices", 
                                        alternate_names =["choices"],
                                        mandatory_columns = [ColumnMapping(standard_name='list_name'),
                                                            ColumnMapping(standard_name='name')])                              
   ],
        schema_unloaded_sheets=[]
    )



@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "gender": ['male', 'male', 'female', 'female', 'other'],
        "items":['rice pasta', 'pasta super_food', 'flour', 'rice', 'flour rice'],
        "question3":[1, 2, 3, 4, 5],
    })


    df_survey = pl.DataFrame({
        "type": ['select_one gender', 'select_multiple item', 'integer'],
        "name":['gender', 'items', 'question3']
    })

    df_choices = pl.DataFrame({
        "list_name": ['gender', 'gender', 'gender', 'item', 'item', 'item', 'item'],
        "name":['male', 'female', 'other', 'rice','pasta', 'flour', 'super_food']
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2", 'question3', 'other'],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="kobo_survey",
                        data_sheet_name="kobo_survey",
                        data=df_survey,
                        data_columns=["type", "name"],
                        column_map=[ColumnMap(schema_column_name = 'type',
                                   data_column_name='type'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')]),
                        SheetMap(
                        schema_sheet_name="kobo_choices",
                        data_sheet_name="kobo_choices",
                        data=df_choices,
                        data_columns=["list_name", "name"],
                        column_map=[ColumnMap(schema_column_name = 'list_name',
                                   data_column_name='list_name'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_sheet_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "gender": ['male', 'male', 'female', 'female', 'other'],
        "items":['rice', 'pasta', 'flour', 'rice', 'flour'],
        "question3":[1, 2, 3, 4, 5],
    })


    df_survey = pl.DataFrame({
        "type": ['select_one gender', 'select_multiple item', 'integer'],
        "name":['gender', 'items', 'question3']
    })

    df_choices = pl.DataFrame({
        "list_name": ['gender', 'gender', 'gender', 'item', 'item', 'item'],
        "name":['male', 'female', 'other', 'rice','pasta', 'flour']
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2", 'question3', 'other'],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="kobo_surveyXXX",
                        data_sheet_name="kobo_surveyXXX",
                        data=df_survey,
                        data_columns=["type", "name"],
                        column_map=[ColumnMap(schema_column_name = 'type',
                                   data_column_name='type'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')]),
                        SheetMap(
                        schema_sheet_name="kobo_choices",
                        data_sheet_name="kobo_choices",
                        data=df_choices,
                        data_columns=["list_name", "name"],
                        column_map=[ColumnMap(schema_column_name = 'list_name',
                                   data_column_name='list_name'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def missing_column_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "gender": ['male', 'male', 'female', 'female', 'other'],
        "items":['rice', 'pasta', 'flour', 'rice', 'flour'],
        "question3":[1, 2, 3, 4, 5],
    })


    df_survey = pl.DataFrame({
        "type": ['select_one gender', 'select_multiple item', 'integer'],
        "name":['gender', 'items', 'question3']
    })

    df_choices = pl.DataFrame({
        "list_name": ['gender', 'gender', 'gender', 'item', 'item', 'item'],
        "name":['male', 'female', 'other', 'rice','pasta', 'flour']
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2", 'question3', 'other'],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="kobo_survey",
                        data_sheet_name="kobo_survey",
                        data=df_survey,
                        data_columns=["type", "name"],
                        column_map=[ColumnMap(schema_column_name = 'type',
                                   data_column_name='type'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')]),
                        SheetMap(
                        schema_sheet_name="kobo_choices",
                        data_sheet_name="kobo_choices",
                        data=df_choices,
                        data_columns=["list_name", "name"],
                        column_map=[ColumnMap(schema_column_name = 'list_nameXXX',
                                   data_column_name='list_nameXXX'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_id_column_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "gender": ['male', 'male', 'female', 'female', 'other'],
        "items":['rice pasta', 'pasta', 'flour', 'rice', 'flour rice'],
        "question3":[1, 2, 3, 4, 5],
    })


    df_survey = pl.DataFrame({
        "type": ['select_one gender', 'select_multiple item', 'integer'],
        "name":['gender', 'items', 'question3']
    })

    df_choices = pl.DataFrame({
        "list_name": ['gender', 'gender', 'gender', 'item', 'item', 'item'],
        "name":['male', 'female', 'other', 'rice','pasta', 'flour']
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2", 'question3', 'other'],
                        column_map=[ColumnMap(schema_column_name = 'uuidXXX',
                                   data_column_name='uuidXXX')]),
                        SheetMap(
                        schema_sheet_name="kobo_survey",
                        data_sheet_name="kobo_survey",
                        data=df_survey,
                        data_columns=["type", "name"],
                        column_map=[ColumnMap(schema_column_name = 'type',
                                   data_column_name='type'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')]),
                        SheetMap(
                        schema_sheet_name="kobo_choices",
                        data_sheet_name="kobo_choices",
                        data=df_choices,
                        data_columns=["list_name", "name"],
                        column_map=[ColumnMap(schema_column_name = 'list_name',
                                   data_column_name='list_name'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_select_one_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "gender": ['man', 'male', 'female', 'female', 'other'],
        "items":['rice', 'pasta', 'flour', 'rice', 'flour'],
        "question3":[1, 2, 3, 4, 5],
    })


    df_survey = pl.DataFrame({
        "type": ['select_one gender', 'select_multiple item', 'integer'],
        "name":['gender', 'items', 'question3']
    })

    df_choices = pl.DataFrame({
        "list_name": ['gender', 'gender', 'gender', 'item', 'item', 'item'],
        "name":['male', 'female', 'other', 'rice','pasta', 'flour']
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2", 'question3', 'other'],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="kobo_survey",
                        data_sheet_name="kobo_survey",
                        data=df_survey,
                        data_columns=["type", "name"],
                        column_map=[ColumnMap(schema_column_name = 'type',
                                   data_column_name='type'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')]),
                        SheetMap(
                        schema_sheet_name="kobo_choices",
                        data_sheet_name="kobo_choices",
                        data=df_choices,
                        data_columns=["list_name", "name"],
                        column_map=[ColumnMap(schema_column_name = 'list_name',
                                   data_column_name='list_name'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_select_multiple_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "gender": ['male', 'male', 'female', 'female', 'other'],
        "items":['rice pasta', 'pasta apples', 'flour', 'rice', 'flour'],
        "question3":[1, 2, 3, 4, 5],
    })


    df_survey = pl.DataFrame({
        "type": ['select_one gender', 'select_multiple item', 'integer'],
        "name":['gender', 'items', 'question3']
    })

    df_choices = pl.DataFrame({
        "list_name": ['gender', 'gender', 'gender', 'item', 'item', 'item'],
        "name":['male', 'female', 'other', 'rice','pasta', 'flour']
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2", 'question3', 'other'],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="kobo_survey",
                        data_sheet_name="kobo_survey",
                        data=df_survey,
                        data_columns=["type", "name"],
                        column_map=[ColumnMap(schema_column_name = 'type',
                                   data_column_name='type'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')]),
                        SheetMap(
                        schema_sheet_name="kobo_choices",
                        data_sheet_name="kobo_choices",
                        data=df_choices,
                        data_columns=["list_name", "name"],
                        column_map=[ColumnMap(schema_column_name = 'list_name',
                                   data_column_name='list_name'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_choice_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame({
        "uuid": [1, 2, 3, 4, 5],
        "gender": ['male man', 'male', 'female', 'female', 'other'],
        "items":['rice pasta', 'pasta', 'flour', 'rice', 'flour rice'],
        "question3":[1, 2, 3, 4, 5],
    })


    df_survey = pl.DataFrame({
        "type": ['select_one gender', 'select_multiple item', 'integer'],
        "name":['gender', 'items', 'question3']
    })

    df_choices = pl.DataFrame({
        "list_name": ['gender', 'gender', 'gender', 'item', 'item', 'item'],
        "name":['male man', 'female', 'other', 'rice','pasta', 'flour']
    })
    
    loaded_sheets = [SheetMap(
                        schema_sheet_name="clean_data",
                        data_sheet_name="clean_data",
                        data=df_clean,
                        data_columns=["uuid", "question1", "question2", 'question3', 'other'],
                        column_map=[ColumnMap(schema_column_name = 'uuid',
                                   data_column_name='uuid')]),
                        SheetMap(
                        schema_sheet_name="kobo_survey",
                        data_sheet_name="kobo_survey",
                        data=df_survey,
                        data_columns=["type", "name"],
                        column_map=[ColumnMap(schema_column_name = 'type',
                                   data_column_name='type'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')]),
                        SheetMap(
                        schema_sheet_name="kobo_choices",
                        data_sheet_name="kobo_choices",
                        data=df_choices,
                        data_columns=["list_name", "name"],
                        column_map=[ColumnMap(schema_column_name = 'list_name',
                                   data_column_name='list_name'),
                                   ColumnMap(schema_column_name = 'name',
                                   data_column_name='name')])]
    
    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestDataType:
    def test_valid_data(self, valid_schema_validator: BaseValidator,
                           valid_excel_data: ExcelLoaderData):
        result = valid_schema_validator.validate(valid_excel_data)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_missing_sheet_data(self, valid_schema_validator: BaseValidator,
                           missing_sheet_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_sheet_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column_data(self, valid_schema_validator: BaseValidator,
                           missing_column_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_column_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_id_column_data(self, valid_schema_validator: BaseValidator,
                           missing_id_column_data: ExcelLoaderData):
        result = valid_schema_validator.validate(missing_id_column_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_select_one_data(self, valid_schema_validator: BaseValidator,
                           invalid_select_one_data: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_select_one_data)
        
        assert isinstance(result, list)
        assert len(result) == 1


    def test_invalid_select_multiple_data(self, valid_schema_validator: BaseValidator,
                           invalid_select_multiple_data: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_select_multiple_data)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_choice_data(self, valid_schema_validator: BaseValidator,
                           invalid_choice_data: ExcelLoaderData):
        result = valid_schema_validator.validate(invalid_choice_data)
        
        assert isinstance(result, list)
        assert len(result) == 1