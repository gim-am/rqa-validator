import polars as pl
import pytest

from rqa_validator.loaders.excel_loader import DataSheetMap, ExcelLoaderData
from rqa_validator.models.base import SchemaColumnMap, SchemaSheetMap
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator
from rqa_validator.validators.schema_validators.duplicate_sheet_match_validator import (
    DuplicateSheetMatches,
)


@pytest.fixture
def valid_schema_validator():
    """Create a UniqueColumn validator instance"""
    return DuplicateSheetMatches()


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
                        standard_name="uuid", alternate_names=["uuid", "X_uuid"]
                    )
                ],
            )
        ],
        schema_unloaded_sheets=[],
    )


@pytest.fixture
def valid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )

    loaded_sheet = DataSheetMap(
        schema_sheet_name="raw_data",
        data_sheet_name="raw_data",
        data=df,
        data_columns=["uuid"],
    )

    return ExcelLoaderData(loaded_sheets=[loaded_sheet])


@pytest.fixture
def invalid_excel_data():
    """Create ExcelLoaderData with matching columns"""
    df = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )
    df2 = pl.DataFrame(
        {
            "uuid": [1, 2, 3, 4, 5],
        }
    )

    loaded_sheets = [
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data",
            data=df,
            data_columns=["uuid"],
        ),
        DataSheetMap(
            schema_sheet_name="raw_data",
            data_sheet_name="raw_data2",
            data=df2,
            data_columns=["uuid"],
        ),
    ]

    return ExcelLoaderData(loaded_sheets=loaded_sheets)


class TestMissingSheets:
    def test_valid_schema(
        self, valid_schema_validator: BaseValidator, valid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(valid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_data(
        self, valid_schema_validator: BaseValidator, invalid_excel_data: ExcelLoaderData
    ):
        result = valid_schema_validator.validate(invalid_excel_data)

        assert isinstance(result, list)
        assert len(result) == 1
