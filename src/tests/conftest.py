import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_validation_result():
    """Create a mock ValidationResult"""
    result = Mock()
    result.is_valid = True
    result.message = ""
    result.sheet_name = None
    result.column_name = None
    return result