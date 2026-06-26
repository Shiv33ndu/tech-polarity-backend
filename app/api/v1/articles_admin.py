# app/api/v1/articles.py

from fastapi import APIRouter, status, HTTPException, Depends, Request
from app.services.article_service import ArticleService
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
)

from app.core.security import require_admin
from app.core.rate_limit import limiter

router = APIRouter(prefix="/articles", tags=["Admin"])

# =====================================================
# ADMIN ROUTES 
# =====================================================

@router.get(
    "/admin/list",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit("60/minute")
async def admin_list_articles(
    request: Request,
    page: int = 1,
    limit: int = 10,
    domain_slug: str | None = None,
    status: str | None = None,
    search: str | None = None,
):
    return await ArticleService.list_articles(
        page=page,
        limit=limit,
        domain_slug=domain_slug,
        status=status,
        search=search,
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit("20/minute")
async def create_article(request: Request, payload: ArticleCreate):

    if await ArticleService.article_exists(payload.slug):
        raise HTTPException(
            status_code=409,
            detail="Article with this slug already exists",
        )

    if not await ArticleService.domain_exists(payload.domain_slug):
        raise HTTPException(
            status_code=400,
            detail="Invalid or inactive domain",
        )

    await ArticleService.create_article(payload.model_dump())
    return {"message": "Article created successfully"}


@router.patch(
    "/{slug}",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit("20/minute")
async def update_article(request: Request, slug: str, payload: ArticleUpdate):

    update_data = {
        k: v for k, v in payload.model_dump().items() if v is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    if "domain_slug" in update_data:
        if not await ArticleService.domain_exists(update_data["domain_slug"]):
            raise HTTPException(
                status_code=400,
                detail="Invalid or inactive domain",
            )

    result = await ArticleService.update_article(slug, update_data)

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

    return {"message": "Article updated successfully"}


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit("20/minute")
async def delete_article(request: Request, slug: str):

    result = await ArticleService.delete_article(slug)

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

@router.get(
    "/admin/stats",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)
@limiter.limit("60/minute")
async def admin_article_stats(request: Request,):
    return await ArticleService.get_article_stats()


