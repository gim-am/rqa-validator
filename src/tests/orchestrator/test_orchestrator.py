from src.rqa_validator.models.jmmi import JMMIDataset, JMMIDatasetSchema
from src.rqa_validator.orchestrator.validation_pipeline import ValidationPipeline
import pytest
from pathlib import Path

@pytest.fixture
def run_pipeline():
    return ValidationPipeline()

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
    def test_valid_file_jmmi(self, run_pipeline: ValidationPipeline, valid_file: Path):
        results = run_pipeline.run_all(valid_file, 'jmmi')
        assert len (results) == 9

    def test_valid_file_other(self, run_pipeline: ValidationPipeline, valid_file: Path):
        results = run_pipeline.run_all(valid_file, 'other')
        assert len (results) == 9

    # def test_valid_file_fuzzy(self, valid_schema: JMMIDatasetSchema, valid_file_fuzzy: Path):
    #     data, results = ExcelLoader(valid_schema).load(valid_file_fuzzy)
    #     assert len (results) == 2 

    # def test_invalid_file_fuzzy(self, valid_schema: JMMIDatasetSchema, invalid_file_fuzzy: Path):
    #     data, results = ExcelLoader(valid_schema).load(invalid_file_fuzzy, True)
    #     assert len (results) == 5 