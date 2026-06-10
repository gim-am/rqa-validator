from abc import ABC, abstractmethod

from ..loaders.base_excel_loader import ExcelLoaderData
from ..models.preprocess import lowercase_schema_mappings
from ..validators.base import BaseValidator, ValidationResult
from .base_dataset_schemas import BaseDatasetSchema


class BaseDataset(ABC):
    def __init__(self) -> None:
        self.schema: BaseDatasetSchema = self.get_schema()
        self.validators: list[BaseValidator] = self.get_validators()
        self.data: ExcelLoaderData

    @abstractmethod
    def get_schema(self) -> BaseDatasetSchema:
        pass

    @abstractmethod
    def get_validators(self) -> list[BaseValidator]:
        pass

    def lower_schema(self, schema: BaseDatasetSchema):
        lowercase_schema_mappings(schema)

    @abstractmethod
    def process_data(self) -> list[ValidationResult]:
        pass

    # TODO: add list of base validators here and use this in child
    # classes as a default list
