import traceback
from pathlib import Path
from typing import Any

from fastexcel import CalamineCellError

from rqa_validator.config import settings

from ..loaders.base import DataSheetMap
from ..loaders.excel_loader import ExcelLoader, ExcelLoaderData
from ..models.base_dataset import BaseDatasetSchema, DynamicDatasetSchema
from ..models.dynamic_model import DynamicDataset
from ..models.jmmi import JMMIDataset
from ..models.preprocess import lowercase_schema_mappings, validate_schema
from ..utils.il8n import i18n
from ..validators.base import BaseValidator, SeverityLevel, ValidationResult


class ValidationPipeline:
    def __init__(self, dataset_type: str):
        self.dataset_type = dataset_type.lower()
        self._setup_schema()
        self.set_errors = set([SeverityLevel.ADMIN_ERROR, SeverityLevel.ERROR])

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

    def run_all(self, filepath: Path, locale: str = "en") -> dict[str, Any]:
        token = i18n.set_locale(locale)
        results = self.run(filepath)
        i18n.reset_locale(token)
        return self._compile_results(results)

    def run(self, filepath: Path) -> list[ValidationResult]:
        """Orchestrator for the dataset validation pipeline.

        Args:
            filepath (Path): Currently the excel filepath. Probably change to api
            call later.

        Returns:
            Dict[str, Any]: JSON results.

        """
        all_results: list[ValidationResult] = []

        # pre-validate the schema. checks for duplicate sheet/column
        # names etc
        try:
            validation_errors = validate_schema(self.schema)

            if validation_errors:
                all_results.extend(validation_errors)
                return all_results
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
            return all_results

        # load the excel data
        try:
            loader = ExcelLoader(self.schema)
            data, excel_results = loader.load(
                filepath,
                load_all_sheets=self.dataset_type == "other",
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
                return all_results

            all_results.append(
                ValidationResult(
                    rule="ExcelFileLoading",
                    message="Data mapping after data load.",
                    severity=SeverityLevel.ADMIN_INFO,
                    details=self._excel_loader_to_dict(data),
                )
            )
        except CalamineCellError as ce:
            all_results.append(
                ValidationResult(
                    rule="ExcelFileLoading",
                    message=f"Loading of the excel file '{filepath.name}'"
                    f" encountered an error. Check that the excel sheets do not contain"
                    f" empty columns without headers: {str(ce)}",
                    severity=SeverityLevel.ERROR,
                )
            )
            settings.logger.log_exception(ce)
            return all_results
        except Exception as e:
            all_results.append(
                ValidationResult(
                    rule="ExcelFileLoading",
                    message=f"Loading of the excel file '{filepath.name}'"
                    f" encountered an error: {str(e)}",
                    severity=SeverityLevel.ADMIN_ERROR,
                )
            )
            settings.logger.log_exception(e)
            return all_results

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

                if not [item for item in results if item.severity in self.set_errors]:
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
                        message=f"Validator '{validator.name}' encountered an error:"
                        f" {traceback.format_exc()}",
                        severity=SeverityLevel.ADMIN_ERROR,
                        details=self._get_validator_params(validator),
                    )
                )
                settings.logger.log_exception(e)

        return all_results

    def _compile_results(self, results: list[ValidationResult]) -> dict[str, Any]:
        """Compile validation results into structured output."""
        buckets: dict[str, list[dict[str, Any]]] = {level.value: [] for level in SeverityLevel}
        counts: dict[str, int] = {level.value: 0 for level in SeverityLevel}
        error_count: int = 0

        for result in results:
            was_truncated = False
            if result.details and settings.LIMIT_DETAILS_THRESHOLD > 0:
                # if the number of details needs to be lmited
                for key, value in result.details.items():
                    # checks to see if the value is a list and if it has too many items.
                    if isinstance(value, list) and len(value) > settings.LIMIT_DETAILS_THRESHOLD:
                        # truncate the list
                        result.details[key] = value[: settings.LIMIT_DETAILS_THRESHOLD]
                        was_truncated = True

                # update message
                if was_truncated:
                    result.message = (
                        f"{result.message} (Details limited to "
                        f"{settings.LIMIT_DETAILS_THRESHOLD} records.)"
                    )

            counts[result.severity.value] += 1

            if result.severity in self.set_errors:
                error_count += 1

            buckets[result.severity.value].append(
                {
                    "rule": result.rule,
                    "message": result.message,
                    "severity": result.severity.value,
                    "sheet_name": result.sheet_name,
                    "column_name": result.column_name,
                    "details": result.details,
                }
            )

        success = error_count == 0

        return {
            "success": success,
            "summary": counts,
            **{key: buckets[key] for key in buckets},
            "metadata": {
                "dataset_type": self.dataset_type,
            },
        }

    def _get_validator_params(self, validator: BaseValidator) -> dict[str, Any]:
        """Get validator paramaters for logs but exclude schema."""
        return {k: v for k, v in vars(validator).items() if not isinstance(v, BaseDatasetSchema)}

    def _excel_loader_to_dict(self, excel_loader: ExcelLoaderData) -> dict[str, Any]:
        """Convert ExcelLoaderData to dict, excluding data and column fields."""

        def data_sheet_map_to_dict(data_sheet: DataSheetMap) -> dict[str, Any]:
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
