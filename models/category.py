# app/models/category.py

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from bson import ObjectId


class Category:
    def __init__(
        self,
        name: str,
        slug: str,
        order: int = 0,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
    ):
        self.name = name              # "Artificial Intelligence"
        self.slug = slug              # "ai"
        self.order = order
        self.is_active = is_active
        self.created_at = created_at or datetime.now(ZoneInfo("Asia/Kolkata"))
