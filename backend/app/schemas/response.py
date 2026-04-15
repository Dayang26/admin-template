# app/schemas/response.py
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """统一 API 响应结构"""

    code: int = 200
    message: str = "success"
    data: T | None = None

    @classmethod
    def ok(cls, data: T = None, code: int = 200, message: str = "success") -> "Response[T]":
        return cls(code=code, message=message, data=data)
