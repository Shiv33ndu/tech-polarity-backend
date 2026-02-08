
from datetime import datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., example="Artificial Intelligence")
    slug: str = Field(..., example="ai")
    order: int = 0
    is_active: bool = True


class CategoryResponse(CategoryBase):
    created_at: datetime


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    order: int | None = None
    is_active: bool | None = None
