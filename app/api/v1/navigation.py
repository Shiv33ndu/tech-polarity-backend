# app/api/v1/navigation.py
"""
Powers:
- Header menu (public)
- Domain filtering (public)
- CMS category management (admin)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.category import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
)
from app.services.category_service import CategoryService
from app.core.security import require_admin

router = APIRouter(prefix="/navigation", tags=["Navigation"])


# PUBLIC — Header Domains
@router.get("/main", response_model=list[CategoryResponse])
async def get_navigation_domains():
    return await CategoryService.get_active_categories()


# ADMIN — Create Domain
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_category(payload: CategoryCreate):
    if await CategoryService.category_exists(payload.slug):
        raise HTTPException(
            status_code=409,
            detail="Category with this slug already exists",
        )

    await CategoryService.create_category(payload.model_dump())
    return {"message": "Category created successfully"}


# ADMIN — Update Domain
@router.patch("/{slug}", dependencies=[Depends(require_admin)])
async def update_category(slug: str, payload: CategoryUpdate):
    update_data = {
        k: v for k, v in payload.model_dump().items() if v is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    result = await CategoryService.update_category(slug, update_data)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category updated successfully"}


# ADMIN — Delete Domain
@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_category(slug: str):
    result = await CategoryService.delete_category(slug)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
