
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ArticleImage(BaseModel):
    url: str
    credit: Optional[str] = None


class ArticleBase(BaseModel):
    title: str
    slug: str
    description: str
    domain: str
    image: ArticleImage
    published_at: datetime


class ArticleSummary(ArticleBase):
    pass


class ArticleDetail(ArticleBase):
    content: str
    tags: List[str]


class RelatedArticle(BaseModel):
    title: str
    slug: str
    description: str
    image: ArticleImage


class TrendingArticle(BaseModel):
    title: str
    slug: str
    description: str
    

class ArticleCreate(BaseModel):
    title: str
    slug: str = Field(..., example="new-gpt-model")
    description: str
    content: str
    domain_slug: str
    tags: List[str] = []
    image: dict
    is_trending: bool = False
    status: str = Field(default="published")


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    domain_slug: Optional[str] = None
    tags: Optional[List[str]] = None
    image: Optional[dict] = None
    is_trending: Optional[bool] = None
    status: Optional[str] = None
