from pathlib import Path

from ..utils.helpers import lowercase_schema_mappings

from ..loaders.excel_loader import ExcelLoader
from ..models.jmmi import JMMIDatasetSchema
from ..validators.base import ValidationResult


class ValidationPipeline:
    def __init__(self, dataset_type: str):
        self.dataset_type = dataset_type
        self._setup_schema()
    
    def _setup_schema(self):
        """Initialize schema and validators based on dataset type."""
        if self.dataset_type == "jmmi":
            self.schema = JMMIDatasetSchema.get_schema()
            self.validators = JMMIDatasetSchema.get_validators(schema=self.schema)
        else:
            raise ValueError(f"Unknown dataset type: {self.dataset_type}")
        
        lowercase_schema_mappings(self.schema)

        

    def run(self, filepath: Path):

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

        return all_results