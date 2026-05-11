from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


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
    sheet_name: str | None = None
    column_name: str | None = None
    details: dict[str, Any] | None = None


class BaseValidator(ABC):
    """Abstract base class for all validators."""

    @abstractmethod
    def validate(self, data: Any) -> list[ValidationResult]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
