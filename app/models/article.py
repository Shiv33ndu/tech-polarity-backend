from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional


class Article:
    def __init__(
        self,
        title: str,
        slug: str,
        description: str,
        content: str,
        domain_slug: str,   # references category.slug
        tags: List[str],
        image: dict,
        is_trending: bool = False,
        status: str = "published",
        published_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.title = title
        self.slug = slug
        self.description = description
        self.content = content
        self.domain_slug = domain_slug
        self.tags = tags
        self.image = image
        self.is_trending = is_trending
        self.status = status
        self.published_at = published_at or datetime.now(ZoneInfo("Asia/Kolkata"))
        self.updated_at = updated_at or datetime.now(ZoneInfo("Asia/Kolkata"))
