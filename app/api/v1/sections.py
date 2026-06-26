# app/api/v1/sections.py
"""
Powers the top (broad) header — News, Tech, AI, Gaming, etc.
Rarely edited, separate from the fine-grained sub-header categories.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.section import (
    SectionResponse,
    SectionCreate,
    SectionUpdate,
)
from app.services.section_service import SectionService
from app.core.security import require_admin

router = APIRouter(prefix="/sections", tags=["Sections"])


# PUBLIC — Top Header Sections
@router.get("/main", response_model=list[SectionResponse])
async def get_main_sections():
    return await SectionService.get_active_sections()


# ADMIN — All Sections (including inactive)
@router.get(
    "/admin/all",
    response_model=list[SectionResponse],
    dependencies=[Depends(require_admin)],
)
async def get_all_sections():
    return await SectionService.get_all_sections()


# ADMIN — Create Section
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_section(payload: SectionCreate):
    if await SectionService.section_exists(payload.slug):
        raise HTTPException(
            status_code=409,
            detail="Section with this slug already exists",
        )

    await SectionService.create_section(payload.model_dump())
    return {"message": "Section created successfully"}


# ADMIN — Update Section
@router.patch("/{slug}", dependencies=[Depends(require_admin)])
async def update_section(slug: str, payload: SectionUpdate):
    update_data = {
        k: v for k, v in payload.model_dump().items() if v is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    result = await SectionService.update_section(slug, update_data)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Section not found")

    return {"message": "Section updated successfully"}


# ADMIN — Delete Section
@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_section(slug: str):
    result = await SectionService.delete_section(slug)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Section not found")
