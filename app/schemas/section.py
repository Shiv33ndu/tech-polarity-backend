
from datetime import datetime
from pydantic import BaseModel, Field


class SectionBase(BaseModel):
    name: str = Field(..., example="Tech")
    slug: str = Field(..., example="tech")
    order: int = 0
    is_active: bool = True


class SectionResponse(SectionBase):
    created_at: datetime


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    name: str | None = None
    order: int | None = None
    is_active: bool | None = None
