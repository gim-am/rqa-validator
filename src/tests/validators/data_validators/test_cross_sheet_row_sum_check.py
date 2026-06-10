import polars as pl
import pytest

from rqa_validator.loaders.base import DataColumnMap
from rqa_validator.loaders.base_excel_loader import ExcelLoaderData
from rqa_validator.loaders.excel_loader import DataSheetMap
from rqa_validator.models.base import SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset_schemas import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.data_validators import (
    CrossSheetRowSumCheck,
)
from tests.helpers import do_basic_checks


@pytest.fixture
def valid_schema_validator(valid_schema):
    """Create a UniqueColumn validator instance"""
    return CrossSheetRowSumCheck(schema=valid_schema)


@pytest.fixture
def valid_schema_child_validator(valid_schema_child):
    """Create a UniqueColumn validator instance"""
    return CrossSheetRowSumCheck(
        schema=valid_schema_child,
        master_sheet="raw_data_child",
        child_sheets=["clean_data_child"],
        master_deletion_log="deletion_log",
    )


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
                        alternate_names=["uuidx", "X_uuid", "uuid2"],
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
                        is_unique=True,
                    )
                ],
            ),
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_schema_child():

    return BaseDatasetSchema(
        dataset_type="jmmi",
        schema_loaded_sheets=[
            SchemaSheetMap(
                standard_name="raw_data_child",
                alternate_names=["raw_data_child"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="person_id",
                        is_unique=True,
                    ),
                    SchemaColumnMap(
                        standard_name="uuid",
                    ),
                ],
                parent_sheet="raw_data",
                parent_linking_column="uuid",
            ),
            SchemaSheetMap(
                standard_name="clean_data_child",
                alternate_names=["clean_data_child"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="person_id",
                        is_unique=True,
                    ),
                    SchemaColumnMap(
                        standard_name="uuid",
                    ),
                ],
            ),
            SchemaSheetMap(
                standard_name="raw_data",
                alternate_names=["raw_data"],
                mandatory_columns=[
                    SchemaColumnMap(
                        standard_name="uuid",
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

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_deleted_data():
    """Create ExcelLoaderData with matching columns"""
    df_raw = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )

    df_deleted = pl.DataFrame(
        {
            "uuid": [],
        }
    )

    df_clean = pl.DataFrame(
        {
            "uuid": [2, 3, 4, 5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_clean_data():
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
            "uuid": [3, 4, 5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw,
        ),
        DataSheetMap(
            schema_sheet_name="clean_data",
            data_sheet_name="clean_data",
            data=df_clean,
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def missing_sheet_data():
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
            "uuid": [3, 4, 5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="bla",
            data_sheet_name="bla",
            data=df_raw,
        ),
        DataSheetMap(
            schema_sheet_name="blo",
            data_sheet_name="blo",
            data=df_clean,
        ),
        DataSheetMap(
            schema_sheet_name="ble",
            data_sheet_name="ble",
            data=df_deleted,
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


@pytest.fixture
def valid_excel_data_child():
    """Create ExcelLoaderData with matching columns"""
    df_raw_child = pl.DataFrame(
        {
            "uuid": [2, 2, 3, 4],
            "person_id": [1, 2, 3, 4],
        }
    )

    df_deleted = pl.DataFrame(
        {
            "uuid": [1],
        }
    )

    df_raw_parent = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )
    df_clean_child = pl.DataFrame(
        {
            "uuid": [2, 2, 3, 4],
            "person_id": [1, 2, 3, 4],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data_child",
            data_sheet_name="raw_data_child",
            data=df_raw_child,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="person_id", data_column_name="person_id"),
            ],
        ),
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df_raw_parent,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="deletion_log",
            data_sheet_name="deletion_log",
            data=df_deleted,
            column_map=[DataColumnMap(schema_column_name="uuid", data_column_name="uuid")],
        ),
        DataSheetMap(
            schema_sheet_name="clean_data_child",
            data_sheet_name="clean_data_child",
            data=df_clean_child,
            column_map=[
                DataColumnMap(schema_column_name="uuid", data_column_name="uuid"),
                DataColumnMap(schema_column_name="person_id", data_column_name="person_id"),
            ],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestCrossSheetRowSum:
    def test_valid_data(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        do_basic_checks(result, 0)

    def test_missing_deleted_data(
        self,
        valid_schema_validator: BaseValidator,
        missing_deleted_data: ExcelLoaderData,
    ):
        result = valid_schema_validator.validate(missing_deleted_data)

        do_basic_checks(result, 1)

    def test_missing_clean_data(
        self, valid_schema_validator: BaseValidator, missing_clean_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_clean_data)

        do_basic_checks(result, 1)

    def test_missing_sheet_data(
        self, valid_schema_validator: BaseValidator, missing_sheet_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(missing_sheet_data)

        do_basic_checks(result, 3)

    def test_parent_child_data(
        self, valid_schema_child_validator: BaseValidator, valid_excel_data_child: ExcelLoaderData
    ):
        result = valid_schema_child_validator.validate(valid_excel_data_child)

        do_basic_checks(result, 0)
