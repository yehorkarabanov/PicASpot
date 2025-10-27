from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseReturn[T](BaseModel):
    message: str
    data: T | None = None
