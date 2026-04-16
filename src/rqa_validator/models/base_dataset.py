from typing import List

from ..models.base import SheetMapping

from ..validators.base import BaseValidator
from abc import abstractmethod, ABC
from dataclasses import dataclass, field

@dataclass
class BaseDatasetSchema:
    dataset_type: str = str()
    # sheets that have to be loaded and used for further validation
    schema_loaded_sheets: List[SheetMapping]= field(default_factory=list)
    # sheets that should exist but dont need to be loaded
    schema_unloaded_sheets: List[SheetMapping]   = field(default_factory=list) 

    def get_schema_sheet(self, sheet_name: str)  -> SheetMapping | None:
        """Gets the details and data for a loaded sheet if it exists.

        Args:
            sheet_name (str): Schema sheets to be searched for

        Returns:
            LoadedSheet | None: Loaded sheet details if found
        """
        for sheet in self.schema_loaded_sheets:
            if sheet.standard_name == sheet_name:
                return sheet
        return None

   



class BaseDataset(ABC):
    @abstractmethod
    def get_schema() -> BaseDatasetSchema:
        pass

    @abstractmethod
    def get_validators() -> List[BaseValidator]:
        pass