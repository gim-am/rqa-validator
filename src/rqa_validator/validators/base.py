from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod



@dataclass
class ValidationResult:
    # passed: bool
    message: str
    severity: str  # 'error', 'warning', 'info'
    sheet_name: Optional[str] = None
    column_name: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    @abstractmethod
    def validate(self, data: Any) -> List[ValidationResult]:
        pass