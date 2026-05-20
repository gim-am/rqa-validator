from rqa_validator.validators.base import SeverityLevel, ValidationResult


def error_counter(results: list[ValidationResult]):
    """Filter out some results to get a list of errors/warnings only."""
    return [
        item
        for item in results
        if item.severity in [SeverityLevel.ERROR, SeverityLevel.ADMIN_ERROR, SeverityLevel.WARNING]
    ]


def do_basic_checks(results: list[ValidationResult], expected: int):
    assert isinstance(results, list)
    assert len(error_counter(results)) == expected
