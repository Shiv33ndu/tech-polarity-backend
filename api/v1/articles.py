# app/api/v1/articles.py

from fastapi import APIRouter, status, HTTPException
from services.article_service import ArticleService
from schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleDetail,
    RelatedArticle,
    TrendingArticle
)

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("/{slug}", response_model=ArticleDetail)
async def get_article(slug: str):
    article = await ArticleService.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/{slug}/related", response_model=list[RelatedArticle])
async def related_articles(slug: str, limit: int = 6):
    article = await ArticleService.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return await ArticleService.get_related_articles(
        domain=article["domain"],
        limit=limit
    )


@router.get("/{slug}/trending", response_model=list[TrendingArticle])
async def trending_articles(slug: str):
    article = await ArticleService.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return await ArticleService.get_trending_by_domain(
        domain=article["domain"]
    )


# ADMIN LEVEL APIs

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    tags=["Admin"]
)
async def create_article(payload: ArticleCreate):

    if await ArticleService.article_exists(payload.slug):
        raise HTTPException(
            status_code=409,
            detail="Article with this slug already exists"
        )

    if not await ArticleService.domain_exists(payload.domain_slug):
        raise HTTPException(
            status_code=400,
            detail="Invalid or inactive domain"
        )

    await ArticleService.create_article(payload.model_dump())
    return {"message": "Article created successfully"}


@router.patch(
    "/{slug}",
    tags=["Admin"]
)
async def update_article(slug: str, payload: ArticleUpdate):

    update_data = {
        k: v for k, v in payload.model_dump().items() if v is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    if "domain_slug" in update_data:
        if not await ArticleService.domain_exists(update_data["domain_slug"]):
            raise HTTPException(
                status_code=400,
                detail="Invalid or inactive domain"
            )

    result = await ArticleService.update_article(slug, update_data)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")

    return {"message": "Article updated successfully"}