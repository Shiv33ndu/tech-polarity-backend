# app/services/article_service.py

from datetime import datetime
from zoneinfo import ZoneInfo
from db import mongo 

ARTICLE_COLLECTION = "articles"
CATEGORY_COLLECTION = "categories"


class ArticleService:

    @staticmethod
    async def get_latest_article(domain_slug: str):
        return await mongo.database[ARTICLE_COLLECTION].find_one(
            {"domain_slug": domain_slug, "status": "published"},
            sort=[("published_at", -1)]
        )

    @staticmethod
    async def get_related_articles(domain_slug: str, limit: int):
        cursor = (
            mongo.database[ARTICLE_COLLECTION]
            .find(
                {
                    "domain_slug": domain_slug,
                    "status": "published"
                }
            )
            .sort("published_at", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    @staticmethod
    async def get_article_by_slug(slug: str):
        return await mongo.database[ARTICLE_COLLECTION].find_one(
            {"slug": slug, "status": "published"}
        )

    @staticmethod
    async def get_trending_by_domain(domain_slug: str, limit: int = 5):
        cursor = (
            mongo.database[ARTICLE_COLLECTION]
            .find(
                {
                    "domain_slug": domain_slug,
                    "is_trending": True,
                    "status": "published"
                }
            )
            .sort("published_at", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)


    # 🔹 Most recent article from ANY active domain
    @staticmethod
    async def get_latest_article_any_domain():
        pipeline = [
            {
                "$lookup": {
                    "from": CATEGORY_COLLECTION,
                    "localField": "domain_slug",
                    "foreignField": "slug",
                    "as": "category"
                }
            },
            {"$unwind": "$category"},
            {"$match": {
                "status": "published",
                "category.is_active": True
            }},
            {"$sort": {"published_at": -1}},
            {"$limit": 1}
        ]

        cursor = mongo.database[ARTICLE_COLLECTION].aggregate(pipeline)
        docs = await cursor.to_list(length=1)
        return docs[0] if docs else None

    # 🔹 Older articles excluding main article
    @staticmethod
    async def get_home_related_articles(exclude_slug: str, limit: int):
        return await (
            mongo.database[ARTICLE_COLLECTION]
            .find(
                {
                    "status": "published",
                    "slug": {"$ne": exclude_slug}
                }
            )
            .sort("published_at", -1)
            .limit(limit)
            .to_list(length=limit)
        )

    # 🔹 Trending across ALL domains (Tech Barometer)
    @staticmethod
    async def get_trending_global(limit: int = 10):
        return await (
            mongo.database[ARTICLE_COLLECTION]
            .find(
                {
                    "is_trending": True,
                    "status": "published"
                }
            )
            .sort("published_at", -1)
            .limit(limit)
            .to_list(length=limit)
        )

    
    @staticmethod
    async def get_tech_barometer():
        now = datetime.now(ZoneInfo("Asia/Kolkata"))

        pipeline = [
            {
                "$match": {
                    "status": "published"
                }
            },
            {
                "$addFields": {
                    "hours_since_publish": {
                        "$divide": [
                            {"$subtract": [now, "$published_at"]},
                            1000 * 60 * 60
                        ]
                    }
                }
            },
            {
                "$addFields": {
                    "article_heat": {
                        "$add": [
                            {"$cond": ["$is_trending", 50, 0]},
                            {
                                "$max": [
                                    0,
                                    {"$subtract": [50, "$hours_since_publish"]}
                                ]
                            }
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$domain_slug",
                    "total_heat": {"$sum": "$article_heat"}
                }
            },
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "_id",
                    "foreignField": "slug",
                    "as": "category"
                }
            },
            {"$unwind": "$category"},
            {
                "$match": {
                    "category.is_active": True
                }
            }
        ]

        data = await mongo.database.articles.aggregate(pipeline).to_list(length=None)

        if not data:
            return []

        # Normalize to 0–100
        max_heat = max(d["total_heat"] for d in data)

        for d in data:
            d["score"] = round((d["total_heat"] / max_heat) * 100)

        return data
    

    # ADMIN CMS LEVEL (Write operations)

    @staticmethod
    async def create_article(data: dict):
        data["published_at"] = datetime.now(ZoneInfo("Asia/Kolkata"))
        data["updated_at"] = datetime.now(ZoneInfo("Asia/Kolkata"))
        return await mongo.database.articles.insert_one(data)

    @staticmethod
    async def update_article(slug: str, data: dict):
        data["updated_at"] = datetime.now(ZoneInfo("Asia/Kolkata"))
        return await mongo.database.articles.update_one(
            {"slug": slug},
            {"$set": data}
        )

    @staticmethod
    async def article_exists(slug: str) -> bool:
        return (
            await mongo.database.articles.count_documents({"slug": slug}) > 0
        )

    @staticmethod
    async def domain_exists(domain_slug: str) -> bool:
        return (
            await mongo.database.categories.count_documents(
                {"slug": domain_slug, "is_active": True}
            )
            > 0
        )