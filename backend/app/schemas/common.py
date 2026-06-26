from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel):
    """统一 API 响应格式。"""
    code: int = 200
    message: str = "success"
    data: Any = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式。"""
    items: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class PaginationParams(BaseModel):
    """分页请求参数。"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
