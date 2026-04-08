from pathlib import Path
from typing import List, Dict, Any
from ..utils.helpers import lowercase_schema_mappings

from ..loaders.excel_loader import ExcelLoader
from ..models.jmmi import JMMIDatasetSchema
from ..validators.base import ValidationResult


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
            self.schema = JMMIDatasetSchema.get_schema()
            self.validators = JMMIDatasetSchema.get_validators(schema=self.schema)
        else:
            raise ValueError(f"Unknown dataset type: {self.dataset_type}")
        
        # make sure all the sheet and column names in the shema are lower
        # to make comparison easier later
        lowercase_schema_mappings(self.schema)        

    def run(self, filepath: Path):
        """Orchestrator for the dataset validation pipeline.

        Args:
            filepath (Path): Currently the excel filepath. Probably change to api
            call later.

        Returns:
            _type_: 
        """
        loader = ExcelLoader(self.schema)
        data = loader.load(filepath)

        if not data:
            return self._create_error_result("No matching sheets found in Excel file")
        
        all_results = []
        for validator in self.validators:
            try:
                results = validator.validate(data)
                if results:
                    all_results.extend(results)
            except Exception as e:
                all_results.append(ValidationResult(
                    # passed=False,
                    message=f"Validator {validator.name} encountered an error: {str(e)}",
                    severity="error"
                ))

        return self._compile_results(all_results)
    
    def _create_error_result(self, message: str) -> Dict[str, Any]:
            return {
                "success": False,
                "errors": [{"message": message, "severity": "error"}],
                "warnings": [],
                "metadata": {"dataset_type": self.dataset_type}
            }

    def _compile_results(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Compile validation results into structured output."""
        errors = [r for r in results if r.severity == "error" ]
        warnings = [r for r in results if r.severity == "warning" ]

        return {
            "success": len(errors) == 0,
            "summary": {
                # "total_checks": len(results),
                # "passed": len(passed),
                "errors": len(errors),
                "warnings": len(warnings)
            },
            "errors": [self._result_to_dict(r) for r in errors],
            "warnings": [self._result_to_dict(r) for r in warnings],
            "metadata": {
                "dataset_type": self.dataset_type,
                # "sheets_processed": list(self.schema.required_columns.keys())
            }
        }

    def _result_to_dict(self, result: ValidationResult) -> Dict[str, Any]:
        """Convert ValidationResult to dictionary for JSON export."""
        return {
            # "passed": result.passed,
            "message": result.message,
            "severity": result.severity,
            # "validator": result.__class__.__name__,
            "sheet_name": result.sheet_name,
            "column_name": result.column_name,
            "details": result.details
        }