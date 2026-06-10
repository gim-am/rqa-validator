import polars as pl
import pytest

from rqa_validator.loaders.base import (
    DataColumnMap,
    DataSheetMap,
)
from rqa_validator.loaders.base_excel_loader import ExcelLoaderData
from rqa_validator.models.base import ProcessValueMap, SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset_schemas import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.data_validators.cleaning_log_to_clean_validator import (
    CleaningLogToClean,
)
from tests.helpers import do_basic_checks, error_counter


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return CleaningLogToClean(schema=valid_schema)


@pytest.fixture
def invalid_schema_validator(invalid_schema):
    """Create a UniqueColumn validator instance"""
    return CleaningLogToClean(schema=invalid_schema)


@pytest.fixture
def invalid_schema2_validator(invalid_schema2):
    """Create a UniqueColumn validator instance"""
    return CleaningLogToClean(schema=invalid_schema2)


@pytest.fixture
def invalid_schema4_validator(invalid_schema4):
    """Create a UniqueColumn validator instance"""
    return CleaningLogToClean(schema=invalid_schema4)


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
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuidx", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="cleaning_log",
                alternate_names=["cleaning_log"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"]),
                    SchemaColumnMap(standard_name="new_value"),
                    SchemaColumnMap(standard_name="old_value"),
                    SchemaColumnMap(standard_name="question"),
                    SchemaColumnMap(
                        standard_name="change_type",
                        alternate_names=["changed"],
                        process_values=[
                            ProcessValueMap(
                                process_name="cleaning_log_validation",
                                values=["yes", "change_response"],
                            )
                        ],
                    ),
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def invalid_schema():

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
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuidx", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="cleaning_log",
                alternate_names=["cleaning_log"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"]),
                    SchemaColumnMap(standard_name="new_value"),
                    SchemaColumnMap(standard_name="old_value"),
                    SchemaColumnMap(standard_name="question"),
                    SchemaColumnMap(standard_name="change_type"),
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def invalid_schema2():

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
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuidx", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="cleaning_logxxx",
                alternate_names=["cleaning_logxxx"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"]),
                    SchemaColumnMap(standard_name="new_value"),
                    SchemaColumnMap(standard_name="old_value"),
                    SchemaColumnMap(standard_name="question"),
                    SchemaColumnMap(standard_name="change_type"),
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def invalid_schema4():

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
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuidmiss",
                        alternate_names=["uuidx", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="cleaning_log",
                alternate_names=["cleaning_log"],
                mandatory_columns=[
                    SchemaColumnMap(standard_name="uuid", alternate_names=["uuid", "X_uuid"]),
                    SchemaColumnMap(standard_name="new_value"),
                    SchemaColumnMap(standard_name="old_value"),
                    SchemaColumnMap(standard_name="question"),
                    SchemaColumnMap(
                        standard_name="change_type",
                        alternate_names=["changed"],
                        process_values=[
                            ProcessValueMap(
                                process_name="cleaning_log_validation",
                                values=["yes", "change_response"],
                            )
                        ],
                    ),
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
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_clean_data_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 7],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_cleanlog_data_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [7],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_question_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question6": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_question_log_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question6"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_sheet_1_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_datamis",
            data_sheet_name="clean_datamis",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_sheet_2_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_logmiss",
            data_sheet_name="cleaning_logmiss",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_1_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuidmiss": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            column_map=[DataColumnMap(schema_column_name="uuidmiss", data_column_name="uuidmiss")],
        ),
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_2_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuidmiss": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuidmiss", data_column_name="uuidmiss"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_3_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_valuemiss": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_valuemiss", data_column_name="new_valuemiss"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_4_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuidmiss": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "questionmiss": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="questionmiss", data_column_name="questionmiss"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_column_5_excel_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_valueXXX", data_column_name="old_valueXXX"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def multi_entry_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5, 5],
            "question": ["question1", "question1"],
            "new_value": [5, 6],
            "old_value": [4, 4],
            "change_type": ["change_response", "change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def valid_excel_data_empty_value():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["4", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [1],
            "question": ["question2"],
            "new_value": [""],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def invalid_excel_data_empty_value():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["4", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [1],
            "question": ["question2"],
            "new_value": [""],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_change_type():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def same_old_data():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "old_value": [5],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_old_data_column():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "question": ["question1"],
            "new_value": [5],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="question", data_column_name="question"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_question_column():
    """Create ExcelLoaderData with matching columns"""

    df_clean = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 5],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
            "question1": [1, 2, 3, 4, 4],
            "question2": ["a", "c", "f", "a", "a"],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
            "questionmiss": ["question1"],
            "new_value": [5],
            "old_value": [4],
            "change_type": ["change_response"],
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
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="new_value", data_column_name="new_value"),
                DataColumnMap(schema_column_name="questionmiss", data_column_name="questionmiss"),
                DataColumnMap(schema_column_name="change_type", data_column_name="change_type"),
                DataColumnMap(schema_column_name="old_value", data_column_name="old_value"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestCleaningLog:
    def test_valid_data(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 0)

    def test_invalid_cleanlog_data(
        self,
        valid_schema_validator: BaseValidator,
        invalid_cleanlog_data_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_cleanlog_data_excel_data)
        filtered_results = error_counter(result)
        do_basic_checks(filtered_results, 1)
        assert filtered_results[0].details is not None
        assert len(filtered_results[0].details["uuid"]) == 1

    def test_invalid_clean_data(
        self,
        valid_schema_validator: BaseValidator,
        invalid_clean_data_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_clean_data_excel_data)
        filtered_results = error_counter(result)
        do_basic_checks(filtered_results, 1)
        assert filtered_results[0].details is not None
        assert len(filtered_results[0].details["uuid"]) == 1

    def test_missing_question_clean_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_question_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_question_excel_data)

        do_basic_checks(result, 1)

    def test_missing_question_log_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_question_log_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_question_log_data)

        do_basic_checks(result, 1)

    def test_missing_sheet_1_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_sheet_1_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_sheet_1_excel_data)

        do_basic_checks(result, 1)

    def test_missing_sheet_2_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_sheet_2_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_sheet_2_excel_data)

        do_basic_checks(result, 1)

    # def test_missing_column_1_data(
    #     self,
    #     valid_schema_validator: BaseValidator,
    #     missing_column_1_excel_data: ExcelLoaderData,
    # ):
    #     result = valid_schema_validator.validate(missing_column_1_excel_data)

    #     assert isinstance(result, list)
    #     assert len(error_counter(result)) == 1

    def test_missing_column_2_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_column_2_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_column_2_excel_data)

        do_basic_checks(result, 1)

    def test_missing_column_3_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_column_3_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_column_3_excel_data)

        do_basic_checks(result, 1)

    def test_missing_column_4_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_column_4_excel_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_column_4_excel_data)

        do_basic_checks(result, 1)

    def test_missing_column_5_data(
        self,
        invalid_schema4_validator: BaseValidator,
        missing_column_5_excel_data: ExcelLoaderData,
    ):
        result = invalid_schema4_validator.validate(missing_column_5_excel_data)

        do_basic_checks(result, 1)

    def test_multientry_data(
        self, valid_schema_validator: BaseValidator, multi_entry_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(multi_entry_data)

        do_basic_checks(result, 1)

    def test_empty_value_data(
        self,
        valid_schema_validator: BaseValidator,
        valid_excel_data_empty_value: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(valid_excel_data_empty_value)

        do_basic_checks(result, 0)

    def test_empty_value_data_invalid(
        self,
        valid_schema_validator: BaseValidator,
        invalid_excel_data_empty_value: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(invalid_excel_data_empty_value)

        do_basic_checks(result, 1)

    def test_missing_change_type_column(
        self,
        valid_schema_validator: BaseValidator,
        missing_change_type: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_change_type)

        do_basic_checks(result, 1)

    def test_invalid_schema(
        self, invalid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = invalid_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 1)

    def test_invalid_schema2(
        self,
        invalid_schema2_validator: BaseValidator,
        valid_excel_data: ExcelLoaderData,
    ):
        result = invalid_schema2_validator.validate(valid_excel_data)

        do_basic_checks(result, 1)
        #  missing columns, multiple edits

    def test_same_old_new_value(
        self, valid_schema_validator: BaseValidator, same_old_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(same_old_data)

        do_basic_checks(result, 1)

    def test_missing_old_value_column(
        self,
        valid_schema_validator: BaseValidator,
        missing_old_data_column: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_old_data_column)

        do_basic_checks(result, 1)

    def test_missing_question_column(
        self,
        valid_schema_validator: BaseValidator,
        missing_question_column: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_question_column)

        do_basic_checks(result, 1)
