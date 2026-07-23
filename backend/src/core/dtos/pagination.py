from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, description="Items per page")


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    page: int
    limit: int
    items: List[T]
    page_count: int
    total_count: int
