import pytest
import polars as pl

from rqa_validator.models.base import ProcessValueMap, SchemaSheetMap, SchemaColumnMap
from rqa_validator.loaders.excel_loader import (
    DataColumnMap,
    DataSheetMap,
    ExcelLoaderData,
)
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.data_validators.column_data_type_validator import (
    DataTypeCheck,
)
from rqa_validator.validators.base import BaseValidator


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return DataTypeCheck(schema=valid_schema)


@pytest.fixture
def schema_missing_column1_validator(schema_missing_column1):
    """Create a UniqueColumn validator instance"""
    return DataTypeCheck(schema=schema_missing_column1)


@pytest.fixture
def schema_missing_column2_validator(schema_missing_column2):
    """Create a UniqueColumn validator instance"""
    return DataTypeCheck(schema=schema_missing_column2)


@pytest.fixture
def schema_missing_sheet1_validator(schema_missing_sheet1):
    """Create a UniqueColumn validator instance"""
    return DataTypeCheck(schema=schema_missing_sheet1)


@pytest.fixture
def schema_missing_sheet2_validator(schema_missing_sheet2):
    """Create a UniqueColumn validator instance"""
    return DataTypeCheck(schema=schema_missing_sheet2)


@pytest.fixture
def schema_missing_process1_validator(schema_missing_process1):
    """Create a UniqueColumn validator instance"""
    return DataTypeCheck(schema=schema_missing_process1)


@pytest.fixture
def schema_missing_process2_validator(schema_missing_process2):
    """Create a UniqueColumn validator instance"""
    return DataTypeCheck(schema=schema_missing_process2)


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
                standard_name="kobo_survey",
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
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def schema_missing_sheet1():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="clean_dataxxx",
                alternate_names=["clean_dataxxx"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuidx", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="kobo_survey",
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
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def schema_missing_sheet2():

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
                standard_name="kobo_surveyxxx",
                alternate_names=["surveyxxx"],
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
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def schema_missing_column1():

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
                standard_name="kobo_survey",
                alternate_names=["survey"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="typexxx",
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
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def schema_missing_column2():

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
                standard_name="kobo_survey",
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
                    SchemaColumnMap(standard_name="namexxx"),
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def schema_missing_process1():

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
                standard_name="kobo_survey",
                alternate_names=["survey"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="type",
                        process_values=[
                            ProcessValueMap(
                                process_name="data_type_numeric_checkxxx",
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
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def schema_missing_process2():

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
                standard_name="kobo_survey",
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
                                process_name="data_type_temporal_check", values=[]
                            ),
                        ],
                    ),
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
            "question1": [1, 2, 3, 4, 5],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_sheet():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_surveyxxx",
            data_sheet_name="kobo_surveyxxx",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_sheet2():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_dataxxx",
            data_sheet_name="clean_dataxxx",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column1():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuidxxx", data_column_name="uuidxxx")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column2():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="typexxx", data_column_name="typexxx"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column3():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="namexxx", data_column_name="namexxx"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": ["1", "2", "3", "4", "nope"],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data2():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": ["1", "2", "3", "4", "5"],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "nope",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
                DataColumnMap(schema_column_name="name", data_column_name="name"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data3():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": ["1", "2", "3", "asdf", "5"],
            "question2": [1.5, 26.6, 3.7, 4.8, 5],
            "question3": [
                "nope",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
            ],
            "other": ["qwe", "wer", "qtr", "asdf", "23432"],
        }
    )

    df_survey = pl.DataFrame(
        {
            "type": ["integer", "decimal", "date"],
            "name": ["question1", "question2", "question3"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "question1", "question2", "question3", "other"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid")
            ],
        ),
        DataSheetMap(
            schema_sheet_name="kobo_survey",
            data_sheet_name="kobo_survey",
            data=df_survey,
            data_columns=["type", "name"],
            column_map=[
                DataColumnMap(schema_column_name="type", data_column_name="type"),
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

        assert isinstance(result, list)
        assert len(result) == 0

    def test_missing_sheet_data(
        self, valid_schema_validator: BaseValidator, missing_sheet: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_sheet)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_sheet2_data(
        self, valid_schema_validator: BaseValidator, missing_sheet2: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_sheet2)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column_data(
        self, valid_schema_validator: BaseValidator, missing_column1: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_column1)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column2_data(
        self, valid_schema_validator: BaseValidator, missing_column2: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_column2)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column3_data(
        self, valid_schema_validator: BaseValidator, missing_column3: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_column3)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_sheet1_schema(
        self,
        schema_missing_sheet1_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = schema_missing_sheet1_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_sheet2_schema(
        self,
        schema_missing_sheet2_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = schema_missing_sheet2_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column1_schema(
        self,
        schema_missing_column1_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = schema_missing_column1_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_column2_schema(
        self,
        schema_missing_column2_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = schema_missing_column2_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_process1_schema(
        self,
        schema_missing_process1_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = schema_missing_process1_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_missing_process2_schema(
        self,
        schema_missing_process2_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = schema_missing_process2_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_invalid_data(
        self, valid_schema_validator: BaseValidator, invalid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(invalid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].details is not None
        assert len(result[0].details["uuid"]) == 1

    def test_invalid_data2(
        self,
        valid_schema_validator: BaseValidator,
        invalid_excel_data2: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_excel_data2)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].details is not None
        assert len(result[0].details["uuid"]) == 1

    def test_invalid_data3(
        self,
        valid_schema_validator: BaseValidator,
        invalid_excel_data3: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_excel_data3)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].details is not None
        assert result[1].details is not None
        assert len(result[0].details["uuid"]) == 1
        assert len(result[1].details["uuid"]) == 1
