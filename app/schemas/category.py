
from datetime import datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., example="Artificial Intelligence")
    slug: str = Field(..., example="ai")
    section_slug: str | None = Field(default=None, example="tech")
    order: int = 0
    is_active: bool = True


class CategoryResponse(CategoryBase):
    created_at: datetime


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    section_slug: str | None = None
    order: int | None = None
    is_active: bool | None = None
