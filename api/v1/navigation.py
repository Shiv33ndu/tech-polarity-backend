# app/api/v1/navigation.py
"""
This file powers:
- Header menu
- Domain filtering
- CMS-style editing (future admin UI)
"""

from fastapi import APIRouter, HTTPException, status
from schemas.category import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
)
from services.category_service import CategoryService

router = APIRouter(prefix="/navigation", tags=["Navigation"])


# PUBLIC — Header Domains
@router.get("/main", response_model=list[CategoryResponse])
async def get_navigation_domains():
    return await CategoryService.get_active_categories()


# ADMIN — Create Domain
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
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
@router.patch("/{slug}")
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
@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(slug: str):
    result = await CategoryService.delete_category(slug)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
