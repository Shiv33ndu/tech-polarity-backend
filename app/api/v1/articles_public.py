from fastapi import APIRouter, status, HTTPException, Depends, Request
from app.services.article_service import ArticleService
from app.schemas.article import (
    ArticleDetail,
    RelatedArticle,
    TrendingArticle
)


router = APIRouter(prefix="/articles", tags=["Articles"])


# =====================================================
# PUBLIC ROUTES
# =====================================================

@router.get("/category/{domain_slug}", tags=["Articles"])
async def articles_by_category(domain_slug: str, page: int = 1, limit: int = 12):
    return await ArticleService.get_articles_by_domain(
        domain_slug=domain_slug,
        page=page,
        limit=limit,
    )


@router.get("/section/{section_slug}", tags=["Articles"])
async def articles_by_section(section_slug: str, page: int = 1, limit: int = 12):
    return await ArticleService.get_articles_by_section(
        section_slug=section_slug,
        page=page,
        limit=limit,
    )


@router.get("/search", tags=["Articles"])
async def search_articles(q: str, page: int = 1, limit: int = 12):
    return await ArticleService.search_articles(
        query=q,
        page=page,
        limit=limit,
    )


@router.get("/{slug}", response_model=ArticleDetail, tags=["Articles"])
async def get_article(slug: str):
    article = await ArticleService.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/{slug}/related", response_model=list[RelatedArticle], tags=["Articles"])
async def related_articles(slug: str, limit: int = 6):
    article = await ArticleService.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return await ArticleService.get_related_articles(
        domain_slug=article["domain_slug"],
        limit=limit,
    )


@router.get("/{slug}/trending", response_model=list[TrendingArticle], tags=["Articles"])
async def trending_articles(slug: str):
    article = await ArticleService.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return await ArticleService.get_trending_by_domain(
        domain_slug=article["domain_slug"]
    )
