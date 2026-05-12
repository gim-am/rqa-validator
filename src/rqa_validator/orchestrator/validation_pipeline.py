from pathlib import Path
from typing import Any

from config import settings

from ..loaders.base import DataSheetMap
from ..loaders.excel_loader import ExcelLoader, ExcelLoaderData
from ..models.base_dataset import BaseDatasetSchema, DynamicDatasetSchema
from ..models.dynamic_model import DynamicDataset
from ..models.jmmi import JMMIDataset
from ..models.preprocess import lowercase_schema_mappings, validate_schema
from ..validators.base import BaseValidator, SeverityLevel, ValidationResult


class ValidationPipeline:
    def __init__(self, dataset_type: str):
        self.dataset_type = dataset_type.lower()
        self._setup_schema()

    def _setup_schema(self):
        """Initialise schema and validators based on dataset type.

        Raises:
            ValueError: if dataset type not found.
        """
        if self.dataset_type == "jmmi":
            self.schema = JMMIDataset.get_schema()
            self.validators = JMMIDataset.get_validators(schema=self.schema)
        elif self.dataset_type == "other":
            self.schema = DynamicDatasetSchema()
        else:
            raise ValueError(f"Unknown dataset type: {self.dataset_type}")

        # make sure all the sheet and column names in the shema are lower
        # to make comparison easier later
        lowercase_schema_mappings(self.schema)

    def run(self, filepath: Path) -> dict[str, Any]:
        """Orchestrator for the dataset validation pipeline.

        Args:
            filepath (Path): Currently the excel filepath. Probably change to api
            call later.

        Returns:
            Dict[str, Any]: JSON results.

        """
        all_results: list[ValidationResult] = []
        set_errors = set([SeverityLevel.ADMIN_ERROR, SeverityLevel.ERROR])
        # pre-validate the schema. checks for duplicate sheet/column
        # names etc
        try:
            validation_errors = validate_schema(self.schema)

            if validation_errors:
                all_results.extend(validation_errors)
                return self._compile_results(all_results)
        except Exception as e:
            all_results.append(
                ValidationResult(
                    rule="SchemaValidation",
                    message=f"Schema validation encountered an error: {str(e)}",
                    severity=SeverityLevel.ADMIN_ERROR,
                    details=vars(self.schema),
                )
            )
            settings.logger.log_exception(e)
            return self._compile_results(all_results)

        # load the excel data
        try:
            loader = ExcelLoader(self.schema)
            data, excel_results = loader.load(
                filepath,
                load_all_sheets=True if self.dataset_type == "other" else False,
            )

            if excel_results:
                all_results.extend(excel_results)

            if not data:
                all_results.append(
                    ValidationResult(
                        rule="ExcelFileLoading",
                        message=f"No matching sheets found in excel file '{filepath}'.",
                        severity=SeverityLevel.ADMIN_ERROR,
                    )
                )
                return self._compile_results(all_results)

            all_results.append(
                ValidationResult(
                    rule="ExcelFileLoading",
                    message="Data mapping after data load.",
                    severity=SeverityLevel.ADMIN_INFO,
                    details=self._excel_loader_to_dict(data),
                )
            )

        except Exception as e:
            all_results.append(
                ValidationResult(
                    rule="ExcelFileLoading",
                    message=f"Loading of the excel file '{filepath}'"
                    f" encountered an error: {str(e)}",
                    severity=SeverityLevel.ADMIN_ERROR,
                )
            )
            settings.logger.log_exception(e)
            return self._compile_results(all_results)

        if self.dataset_type == "other":
            dataset = DynamicDataset(data)
            results = dataset.process_data()
            if results:
                all_results.extend(results)

            self.validators = dataset.get_validators()
            self.schema = dataset.get_schema()
            data = dataset.data

        all_results.append(
            ValidationResult(
                rule="Schema Details",
                message=f"Schema for dataset '{self.dataset_type}' and file '{filepath}'",
                severity=SeverityLevel.ADMIN_INFO,
                details=vars(self.schema),
            )
        )

        # run each of the validators for the dataset.
        for validator in self.validators:
            try:
                results = validator.validate(data)
                if results:
                    all_results.extend(results)
                elif not [item for item in results if item.severity in set_errors]:
                    all_results.append(
                        ValidationResult(
                            rule=validator.name,
                            message=f"Validator '{validator.name}' passed.",
                            severity=SeverityLevel.PASSED,
                            details=self._get_validator_params(validator),
                        )
                    )
            except Exception as e:
                all_results.append(
                    ValidationResult(
                        rule=validator.name,
                        message=f"Validator '{validator.name}' encountered an error: {str(e)}",
                        severity=SeverityLevel.ADMIN_ERROR,
                        details=self._get_validator_params(validator),
                    )
                )
                settings.logger.log_exception(e)

        return self._compile_results(all_results)

    def _compile_results(self, results: list[ValidationResult]) -> dict[str, Any]:
        """Compile validation results into structured output."""
        errors = [r for r in results if r.severity == SeverityLevel.ERROR]
        admin_errors = [r for r in results if r.severity == SeverityLevel.ADMIN_ERROR]
        warnings = [r for r in results if r.severity == SeverityLevel.WARNING]
        info = [r for r in results if r.severity == SeverityLevel.INFO]
        admin_info = [r for r in results if r.severity == SeverityLevel.ADMIN_INFO]
        passed = [r for r in results if r.severity == SeverityLevel.PASSED]

        return {
            "success": len(errors) == 0 and len(admin_errors) == 0,
            "summary": {
                "passed": len(passed),
                "admin_errors": len(admin_errors),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info),
                "admin_info": len(admin_info),
            },
            "admin_errors": [self._result_to_dict(r) for r in admin_errors],
            "errors": [self._result_to_dict(r) for r in errors],
            "warnings": [self._result_to_dict(r) for r in warnings],
            "info": [self._result_to_dict(r) for r in info],
            "admin_info": [self._result_to_dict(r) for r in admin_info],
            "passed": [self._result_to_dict(r) for r in passed],
            "metadata": {
                "dataset_type": self.dataset_type,
            },
        }

    def _result_to_dict(self, result: ValidationResult) -> dict[str, Any]:
        """Convert ValidationResult to dictionary for JSON export."""
        return {
            "rule": result.rule,
            "message": result.message,
            "severity": result.severity.value,
            "sheet_name": result.sheet_name,
            "column_name": result.column_name,
            "details": result.details,
        }

    def _get_validator_params(self, validator: BaseValidator) -> dict[str, Any]:
        """Get validator paramaters for logs but exclude schema."""
        return {k: v for k, v in vars(validator).items() if not isinstance(v, BaseDatasetSchema)}

    def _excel_loader_to_dict(self, excel_loader: ExcelLoaderData) -> dict:
        """Convert ExcelLoaderData to dict, excluding data and column fields."""

        def data_sheet_map_to_dict(data_sheet: DataSheetMap) -> dict:
            return {
                "schema_sheet_name": data_sheet.schema_sheet_name,
                "data_sheet_name": data_sheet.data_sheet_name,
                "column_map": data_sheet.column_map,
            }

        return {
            "loaded_sheets": [
                data_sheet_map_to_dict(sheet) for sheet in excel_loader.loaded_sheets
            ],
            "unloaded_sheets": [
                data_sheet_map_to_dict(sheet) for sheet in excel_loader.unloaded_sheets
            ],
            "unexpected_sheets": excel_loader.unexpected_sheets,
        }
