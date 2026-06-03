import polars as pl
import pytest

from rqa_validator.loaders.excel_loader import (
    DataColumnMap,
    DataSheetMap,
    ExcelLoaderData,
)
from rqa_validator.models.base import ProcessValueMap, SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.data_validators.survey_choices_validator import (
    SurveyChoicesCheck,
)
from tests.helpers import do_basic_checks


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return SurveyChoicesCheck(schema=valid_schema)


@pytest.fixture
def valid_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="clean_data",
                alternate_names=["clean_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuidx", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="survey",
                alternate_names=["survey"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="type",
                        process_values=[
                            ProcessValueMap(
                                process_name="data_type_numeric_check",
                                values=["integer", "decimal"],
                            ),
                            ProcessValueMap(
                                process_name="data_type_temporal_check", values=["date"]
                            ),
                        ],
                    ),
                    SchemaColumnMap(standard_name="name"),
                ],
            ),
            SchemaSheetMap(
                standard_name="choices",
                alternate_names=["choices"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="list_name"),
                    SchemaColumnMap(standard_name="name"),
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "gender": ["male", "male", "female", "female", "other"],
            "items": ["rice pasta", "pasta super_food", "flour", "rice", "flour rice"],
            "question3": [1, 2, 3, 4, 5],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["select_one gender", "select_multiple item", "integer"],
            "name": ["gender", "items", "question3"],
        }
    )

    df_choices = pl.DataFrame(
        {
            "list_name": ["gender", "gender", "gender", "item", "item", "item", "item"],
            "name": ["male", "female", "other", "rice", "pasta", "flour", "super_food"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="survey",
            data_sheet_name="survey",
            data=df_survey,
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="choices",
            data_sheet_name="choices",
            data=df_choices,
            column_map=[
                DataColumnMap(schema_column_name="list_name", data_column_name="list_name"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_sheet_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "gender": ["male", "male", "female", "female", "other"],
            "items": ["rice", "pasta", "flour", "rice", "flour"],
            "question3": [1, 2, 3, 4, 5],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["select_one gender", "select_multiple item", "integer"],
            "name": ["gender", "items", "question3"],
        }
    )

    df_choices = pl.DataFrame(
        {
            "list_name": ["gender", "gender", "gender", "item", "item", "item"],
            "name": ["male", "female", "other", "rice", "pasta", "flour"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="surveyXXX",
            data_sheet_name="surveyXXX",
            data=df_survey,
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="choices",
            data_sheet_name="choices",
            data=df_choices,
            column_map=[
                DataColumnMap(schema_column_name="list_name", data_column_name="list_name"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "gender": ["male", "male", "female", "female", "other"],
            "items": ["rice", "pasta", "flour", "rice", "flour"],
            "question3": [1, 2, 3, 4, 5],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["select_one gender", "select_multiple item", "integer"],
            "name": ["gender", "items", "question3"],
        }
    )

    df_choices = pl.DataFrame(
        {
            "list_name": ["gender", "gender", "gender", "item", "item", "item"],
            "name": ["male", "female", "other", "rice", "pasta", "flour"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="survey",
            data_sheet_name="survey",
            data=df_survey,
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="choices",
            data_sheet_name="choices",
            data=df_choices,
            column_map=[
                DataColumnMap(schema_column_name="list_nameXXX", data_column_name="list_nameXXX"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_id_column_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "gender": ["male", "male", "female", "female", "other"],
            "items": ["rice pasta", "pasta", "flour", "rice", "flour rice"],
            "question3": [1, 2, 3, 4, 5],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["select_one gender", "select_multiple item", "integer"],
            "name": ["gender", "items", "question3"],
        }
    )

    df_choices = pl.DataFrame(
        {
            "list_name": ["gender", "gender", "gender", "item", "item", "item"],
            "name": ["male", "female", "other", "rice", "pasta", "flour"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuidXXX", data_column_name="uuidXXX")],
        ),
        DataSheetMap(
            schema_sheet_name="survey",
            data_sheet_name="survey",
            data=df_survey,
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="choices",
            data_sheet_name="choices",
            data=df_choices,
            column_map=[
                DataColumnMap(schema_column_name="list_name", data_column_name="list_name"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_select_one_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "gender": ["man", "male", "female", "female", "other"],
            "items": ["rice", "pasta", "flour", "rice", "flour"],
            "question3": [1, 2, 3, 4, 5],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["select_one gender", "select_multiple item", "integer"],
            "name": ["gender", "items", "question3"],
        }
    )

    df_choices = pl.DataFrame(
        {
            "list_name": ["gender", "gender", "gender", "item", "item", "item"],
            "name": ["male", "female", "other", "rice", "pasta", "flour"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="survey",
            data_sheet_name="survey",
            data=df_survey,
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="choices",
            data_sheet_name="choices",
            data=df_choices,
            column_map=[
                DataColumnMap(schema_column_name="list_name", data_column_name="list_name"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_select_multiple_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "gender": ["male", "male", "female", "female", "other"],
            "items": ["rice pasta", "pasta apples", "flour", "rice", "flour"],
            "question3": [1, 2, 3, 4, 5],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["select_one gender", "select_multiple item", "integer"],
            "name": ["gender", "items", "question3"],
        }
    )

    df_choices = pl.DataFrame(
        {
            "list_name": ["gender", "gender", "gender", "item", "item", "item"],
            "name": ["male", "female", "other", "rice", "pasta", "flour"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="survey",
            data_sheet_name="survey",
            data=df_survey,
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="choices",
            data_sheet_name="choices",
            data=df_choices,
            column_map=[
                DataColumnMap(schema_column_name="list_name", data_column_name="list_name"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_choice_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "gender": ["male man", "male", "female", "female", "other"],
            "items": ["rice pasta", "pasta", "flour", "rice", "flour rice"],
            "question3": [1, 2, 3, 4, 5],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["select_one gender", "select_multiple item", "integer"],
            "name": ["gender", "items", "question3"],
        }
    )

    df_choices = pl.DataFrame(
        {
            "list_name": ["gender", "gender", "gender", "item", "item", "item"],
            "name": ["male man", "female", "other", "rice", "pasta", "flour"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="survey",
            data_sheet_name="survey",
            data=df_survey,
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="choices",
            data_sheet_name="choices",
            data=df_choices,
            column_map=[
                DataColumnMap(schema_column_name="list_name", data_column_name="list_name"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestDataType:
    def test_valid_data(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 0)

    def test_missing_sheet_data(
        self, valid_schema_validator: BaseValidator, missing_sheet_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_sheet_data)

        do_basic_checks(result, 1)

    def test_missing_column_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_column_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_column_data)

        do_basic_checks(result, 1)

    def test_missing_id_column_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_id_column_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_id_column_data)

        do_basic_checks(result, 1)

    def test_invalid_select_one_data(
        self,
        valid_schema_validator: BaseValidator,
        invalid_select_one_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_select_one_data)

        do_basic_checks(result, 1)

    def test_invalid_select_multiple_data(
        self,
        valid_schema_validator: BaseValidator,
        invalid_select_multiple_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_select_multiple_data)

        do_basic_checks(result, 1)

    def test_choice_data(
        self,
        valid_schema_validator: BaseValidator,
        invalid_choice_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_choice_data)

        do_basic_checks(result, 1)
