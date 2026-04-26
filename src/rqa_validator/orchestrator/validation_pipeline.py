from pathlib import Path
from typing import List, Dict, Any
from ..models.preprocess import lowercase_schema_mappings, validate_schema

from ..loaders.excel_loader import ExcelLoader
from ..models.jmmi import JMMIDataset
from ..validators.base import ValidationResult

from ..models.test_model import TestModelDataset


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
        elif self.dataset_type == "testmodel":
            self.schema = TestModelDataset.get_schema()
            self.validators = TestModelDataset.get_validators(schema=self.schema)
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
        all_results:List[ValidationResult] = []

        try:            
            validation_errors =  validate_schema(self.schema)  
                
            if validation_errors:
                all_results.extend(validation_errors)
                return self._compile_results(all_results)
        except Exception as e:
            all_results.append(ValidationResult(
                    rule='SchemaValidation',
                    message=f"Schema validation encountered an error: {str(e)}",
                    severity="admin_error"
                ))
            return self._compile_results(all_results)

        try:
            loader = ExcelLoader(self.schema)
            data, excel_results = loader.load(filepath)
            
            if excel_results:   
                all_results.extend(excel_results)

            if not data:
                all_results.append(ValidationResult(
                    rule='ExcelFileLoading',
                    message=f"No matching sheets founf in excel file {filepath}.",
                    severity="admin_error"
                ))
                return self._compile_results(all_results)
        except Exception as e:
            all_results.append(ValidationResult(
                    rule='ExcelFileLoading',
                    message=f"Loading of the excel file {filepath} encountered an error: {str(e)}",
                    severity="admin_error"
                ))
            return self._compile_results(all_results)
        
        for validator in self.validators:
            try:
                results = validator.validate(data)
                if results:
                    all_results.extend(results)
            except Exception as e:
                all_results.append(ValidationResult(
                    rule=validator.name,
                    message=f"Validator {validator.name} encountered an error: {str(e)}",
                    severity="admin_error"
                ))

        return self._compile_results(all_results)
    
    def _create_error_result(self, message: str) -> Dict[str, Any]:
            return {
                "success": False,
                "errors": [{"message": message, "severity": "error"}],
                "warnings": [],
                "info": [],
                "metadata": {"dataset_type": self.dataset_type}
            }

    def _compile_results(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Compile validation results into structured output."""
        errors = [r for r in results if r.severity == "error" ]
        admin_errors = [r for r in results if r.severity == "admin_error" ]
        warnings = [r for r in results if r.severity == "warning" ]
        info = [r for r in results if r.severity == "info" ]


        return {
            "success": len(errors) == 0 and len(admin_errors) == 0,
            "summary": {
                # "total_checks": len(results),
                # "passed": len(passed),
                "admin_errors": len(admin_errors),
                "errors": len(errors),                
                "warnings": len(warnings),
                "info": len(info)
            },
            "admin_errors": [self._result_to_dict(r) for r in admin_errors],
            "errors": [self._result_to_dict(r) for r in errors],            
            "warnings": [self._result_to_dict(r) for r in warnings],
            "info": [self._result_to_dict(r) for r in info],
            "metadata": {
                "dataset_type": self.dataset_type,
                # "sheets_processed": list(self.schema.required_columns.keys())
            }
        }

    def _result_to_dict(self, result: ValidationResult) -> Dict[str, Any]:
        """Convert ValidationResult to dictionary for JSON export."""
        return {
            "rule": result.rule,
            "message": result.message,
            "severity": result.severity,
            # "validator": result.__class__.__name__,
            "sheet_name": result.sheet_name,
            "column_name": result.column_name,
            "details": result.details
        }