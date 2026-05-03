from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    ADMIN_ERROR = "admin_error"
    PASSED = "passed"

@dataclass
class ValidationResult:
    rule: str
    message: str
    severity: SeverityLevel  
    sheet_name: Optional[str] = None
    column_name: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    @abstractmethod
    def validate(self, data: Any) -> List[ValidationResult]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass