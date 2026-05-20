import polars as pl
import pytest

from rqa_validator.loaders.excel_loader import (
    DataColumnMap,
    DataSheetMap,
    ExcelLoaderData,
)
from rqa_validator.models.base import SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.data_validators.cross_sheet_id_check_validator import (
    CrossSheetIdCheck,
)
from tests.helpers import do_basic_checks


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return CrossSheetIdCheck(schema=valid_schema)


@pytest.fixture
def valid_schema():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuid", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
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
                standard_name="deletion_log",
                alternate_names=["deletion_log"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuid", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
            SchemaSheetMap(
                standard_name="cleaning_log",
                alternate_names=["cleaning_log"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
                        alternate_names=["uuid", "X_uuid"],
                        is_unique=True,
                    )
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)

@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    )

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5, 6, 7, 8, 9, 10, 90],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def master_extra_id_column_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5], "uuidx": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid", "uuidx"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="uuid", data_column_name="uuidx"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_extra_id_column_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame({"uuid": [2, 3, 4, 5], "uuidx": [2, 3, 4, 5]})

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid", "uuidx"],
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="uuid", data_column_name="uuidx"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_missing_id_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5, 7],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_missing_id_column():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5, 7],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_missing_sheets_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5, 7],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_dataxxx",
            data_sheet_name="clean_dataxxx",
            data=df_clean,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_logxxx",
            data_sheet_name="deletion_logxxx",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_logxxx",
            data_sheet_name="cleaning_logxxx",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def master_no_id_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuidnomatch": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5, 7],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def child_no_id_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuidnomatch": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5, 7],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def master_missing_sheets_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5, 7],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_datax",
            data_sheet_name="raw_datax",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def no_match_id_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame({"uuid": [1, 2, 3, 4, 5]})

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuidmis": [2, 3, 4, 5, 7],
        }
    )

    df_clean_log = pl.DataFrame(
        {
            "uuid": [5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
            data_columns=["uuidmis"],
            column_map=[DataColumnMap(schema_column_name="uuidmis", data_column_name="uuidmis")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="cleaning_log",
            data_sheet_name="cleaning_log",
            data=df_clean_log,
            data_columns=["uuid"],
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestCrossSheetIdCheck:
    def test_valid_data(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 0)

    def test_invalid_data(
        self, valid_schema_validator: BaseValidator, invalid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(invalid_excel_data)

        do_basic_checks(result, 1)

    def test_master_extra_id_column_data(
        self,
        valid_schema_validator: BaseValidator,
        master_extra_id_column_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(master_extra_id_column_data)

        do_basic_checks(result, 0)

    def test_child_extra_id_column_data(
        self,
        valid_schema_validator: BaseValidator,
        child_extra_id_column_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(child_extra_id_column_data)

        do_basic_checks(result, 0)

    def test_child_extra_id_data(
        self,
        valid_schema_validator: BaseValidator,
        child_missing_id_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(child_missing_id_data)

        do_basic_checks(result, 1)

    def test_child_missing_sheets_data(
        self,
        valid_schema_validator: BaseValidator,
        child_missing_sheets_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(child_missing_sheets_data)

        do_basic_checks(result, 3)

    def test_master_missing_sheets_data(
        self,
        valid_schema_validator: BaseValidator,
        master_missing_sheets_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(master_missing_sheets_data)

        do_basic_checks(result, 1)

    def test_master_no_id_data(
        self, valid_schema_validator: BaseValidator, master_no_id_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(master_no_id_data)

        do_basic_checks(result, 1)

    def test_child_no_id_data(
        self, valid_schema_validator: BaseValidator, master_no_id_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(master_no_id_data)

        do_basic_checks(result, 1)

    def test_child_missing_id_column(
        self,
        valid_schema_validator: BaseValidator,
        child_missing_id_column: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(child_missing_id_column)

        do_basic_checks(result, 1)

    def test_no_match_id_column(
        self, valid_schema_validator: BaseValidator, no_match_id_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(no_match_id_data)

        do_basic_checks(result, 1)
