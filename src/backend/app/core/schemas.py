from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseReturn[T](BaseModel):
    message: str
    data: T | None = None


class ValidationErrorDetail(BaseModel):
    """Standardized validation error detail"""

    field: str
    message: str
    type: str


class ValidationErrorData(BaseModel):
    """Container for validation errors"""

    errors: list[ValidationErrorDetail]


class ValidationErrorReturn(BaseReturn[ValidationErrorData]):
    """Response for validation errors - uses BaseReturn structure"""

    pass
