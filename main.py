import argparse
from pathlib import Path

from rqa_validator.config import settings
from rqa_validator.validators.base import SeverityLevel
from src.rqa_validator.orchestrator.validation_pipeline import ValidationPipeline


def main():
    parser = argparse.ArgumentParser(description="Data Validation Framework")
    parser.add_argument("input_file", type=Path, help="Path to Excel file")
    parser.add_argument(
        "--dataset-type",
        required=True,
        choices=["jmmi", "other"],
        help="Type of dataset to validate",
    )
    # parser.add_argument("--output",
    #                   type=Path, default=Path("validation_results.json"),
    #                    help="Output path for JSON results")

    args = parser.parse_args()

    pipeline = ValidationPipeline()
    results = pipeline.run_all(args.input_file, dataset_type=args.dataset_type)

    print(f"Admin Errors: {results['summary'][SeverityLevel.ADMIN_ERROR.value]}")
    print(f"Errors: {results['summary'][SeverityLevel.ERROR.value]}")
    print(f"Warnings: {results['summary'][SeverityLevel.WARNING.value]}")
    print(f"info: {results['summary'][SeverityLevel.INFO.value]}")
    print(f"admin_info: {results['summary'][SeverityLevel.ADMIN_INFO.value]}")
    print(f"passed: {results['summary'][SeverityLevel.PASSED.value]}")
    print(results[SeverityLevel.ADMIN_ERROR.value])
    print(results[SeverityLevel.ERROR.value])
    print(results[SeverityLevel.WARNING.value])
    print(results[SeverityLevel.INFO.value])
    print(results[SeverityLevel.ADMIN_INFO.value])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        settings.logger.log_exception(e)

    exit()
