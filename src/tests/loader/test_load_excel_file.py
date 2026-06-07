from src.rqa_validator.models.jmmi import JMMIDataset, JMMIDatasetSchema
from src.rqa_validator.loaders.excel_loader import ExcelLoader
import pytest
from pathlib import Path


@pytest.fixture
def valid_schema():
    return JMMIDataset.get_schema()

@pytest.fixture
def valid_file():
    return Path('src/tests/loader/jmmi_valid.xlsx')

@pytest.fixture
def valid_file_fuzzy():
    return Path('src/tests/loader/jmmi_valid_fuzzy.xlsx')

@pytest.fixture
def invalid_file_fuzzy():
    return Path('src/tests/loader/jmmi_invalid_fuzzy.xlsx')



class TestLoadData:
    def test_valid_file(self, valid_schema: JMMIDatasetSchema, valid_file: Path):
        data, results = ExcelLoader(valid_schema).load(valid_file)
        assert len (results) == 0 

    def test_valid_file_fuzzy(self, valid_schema: JMMIDatasetSchema, valid_file_fuzzy: Path):
        data, results = ExcelLoader(valid_schema).load(valid_file_fuzzy)
        assert len (results) == 2 

    def test_invalid_file_fuzzy(self, valid_schema: JMMIDatasetSchema, invalid_file_fuzzy: Path):
        data, results = ExcelLoader(valid_schema).load(invalid_file_fuzzy, True)
        assert len (results) == 5 