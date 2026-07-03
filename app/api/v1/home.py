# app/api/v1/home.py

from fastapi import APIRouter, HTTPException
from app.services.article_service import ArticleService
from app.schemas.article import ArticleSummary, TrendingArticle

router = APIRouter(prefix="/home", tags=["Home"])


@router.get("/main-article", response_model=ArticleSummary)
async def main_article():
    article = await ArticleService.get_latest_article_any_domain()
    if not article:
        raise HTTPException(status_code=404, detail="No articles found")
    return article


@router.get("/related-articles", response_model=list[ArticleSummary])
async def related_articles(
    exclude_slug: str,
    limit: int = 8
):
    return await ArticleService.get_home_related_articles(
        exclude_slug=exclude_slug,
        limit=limit
    )


@router.get("/tech-barometer")
async def tech_barometer():
    data = await ArticleService.get_tech_barometer()

    return [
        {
            "section": d["_id"],
            "label": d["section"]["name"],
            "score": d["score"]
        }
        for d in data
    ]


@router.get("/trending", response_model=list[TrendingArticle])
async def trending_by_domain(domain_slug: str, limit: int = 5):
    return await ArticleService.get_trending_by_domain(
        domain_slug=domain_slug,
        limit=limit
    )


@router.get("/trending-global", response_model=list[TrendingArticle])
async def trending_global(limit: int = 10):
    return await ArticleService.get_trending_global(limit=limit)


@router.get("/trending-by-section", response_model=list[TrendingArticle])
async def trending_by_section(section_slug: str, limit: int = 5):
    return await ArticleService.get_trending_by_section(
        section_slug=section_slug,
        limit=limit
    )
