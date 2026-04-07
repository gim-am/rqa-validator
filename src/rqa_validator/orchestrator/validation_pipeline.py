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

        return all_results
    
