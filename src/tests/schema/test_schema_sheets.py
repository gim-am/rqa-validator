import pytest
from rqa_validator.models.base import SheetMapping, ColumnMapping, BaseDatasetSchema
from rqa_validator.models.preprocess import validate_schema, lowercase_schema_mappings

@pytest.fixture
def valid_schema():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "raw_data", 
                                            alternate_names =["raw_data"],
                                            mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                            alternate_names=["uuid", "X_uuid"])],  
                                            )],
        schema_unloaded_sheets=[SheetMapping(standard_name="read_me", 
                        alternate_names= ["read_me"])]
    )

@pytest.fixture
def invalid_schema():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "raw_data", 
                                            alternate_names =["raw_data"],
                                            mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                            alternate_names=["uuid", "X_uuid"])],  
                                            ),
                            SheetMapping(standard_name= "raw_data", 
                                        alternate_names =["raw_data"],
                                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                        alternate_names=["uuid", "X_uuid"])],  
                                        )],
        schema_unloaded_sheets=[SheetMapping(standard_name="read_me", 
                        alternate_names= ["read_me"])]
    )

@pytest.fixture
def invalid_schema_2():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "raw_data", 
                                            alternate_names =["raw_data"],
                                            mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                            alternate_names=["uuid", "X_uuid"])],  
                                            ),
                            SheetMapping(standard_name= "clean_data", 
                                        alternate_names =["raw_data"],
                                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                        alternate_names=["uuid", "X_uuid"])],  
                                        )],
        schema_unloaded_sheets=[]
    )

@pytest.fixture
def invalid_schema_3():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "raw_data", 
                                            alternate_names =["raw_data"],
                                            mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                            alternate_names=["uuid", "X_uuid"])],  
                                            ),
                            SheetMapping(standard_name= "raw_data", 
                                        alternate_names =["raw_data"],
                                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                        alternate_names=["uuid", "X_uuid"])],  
                                        )],
        schema_unloaded_sheets=[SheetMapping(standard_name="read_me", 
                        alternate_names= ["read_me"]),
                        SheetMapping(standard_name="analysis", 
                        alternate_names= ["read_me"])]
    )

@pytest.fixture
def invalid_schema_4():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "raw_data", 
                                            alternate_names =["raw_data"],
                                            mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                            alternate_names=["uuid", "X_uuid"])],  
                                            ),
                            SheetMapping(standard_name= "raw_data", 
                                        alternate_names =["raw_data"],
                                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                        alternate_names=["uuid", "X_uuid"])],  
                                        )],
        schema_unloaded_sheets=[SheetMapping(standard_name="read_me", 
                        alternate_names= ["read_me"]),
                        SheetMapping(standard_name="raw_data", 
                        alternate_names= ["raw_data"])]
    )

@pytest.fixture
def invalid_schema_5():
    
    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[SheetMapping(standard_name= "raw_data", 
                                            alternate_names =["raw_data"],
                                            mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                            alternate_names=["uuid", "X_uuid"])],  
                                            ),
                            SheetMapping(standard_name= "raw_data", 
                                        alternate_names =["raw_data"],
                                        mandatory_columns= [ColumnMapping(standard_name="uuid",
                                                                        alternate_names=["uuid", "X_uuid"])],  
                                        )],
        schema_unloaded_sheets=[SheetMapping(standard_name="read_me", 
                        alternate_names= ["read_me"]),
                        SheetMapping(standard_name="analysis", 
                        alternate_names= ["raw_data"])]
    )


class TestSchemaSheets:
    def test_valid_schema(self, valid_schema: BaseDatasetSchema):
        lowercase_schema_mappings(valid_schema)
        result = validate_schema(valid_schema)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_schema(self, invalid_schema: BaseDatasetSchema):
        result = validate_schema(invalid_schema)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_schema2(self, invalid_schema_2: BaseDatasetSchema):
        result = validate_schema(invalid_schema_2)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_schema3(self, invalid_schema_3: BaseDatasetSchema):
        result = validate_schema(invalid_schema_3)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_schema4(self, invalid_schema_4: BaseDatasetSchema):
        result = validate_schema(invalid_schema_4)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_schema5(self, invalid_schema_5: BaseDatasetSchema):
        result = validate_schema(invalid_schema_5)
        
        assert isinstance(result, list)
        assert len(result) == 1