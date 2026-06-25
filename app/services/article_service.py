# app/services/article_service.py

from datetime import datetime
from zoneinfo import ZoneInfo
from app.db import mongo 

from app.utils.mongo import serialize_mongo_doc

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
    

    @staticmethod
    async def get_articles_by_domain(domain_slug: str, page: int = 1, limit: int = 12):
        skip = (page - 1) * limit
        query = {"domain_slug": domain_slug, "status": "published"}
        cursor = (
            mongo.database[ARTICLE_COLLECTION]
            .find(query)
            .sort("published_at", -1)
            .skip(skip)
            .limit(limit)
        )
        items = await cursor.to_list(length=limit)
        total = await mongo.database[ARTICLE_COLLECTION].count_documents(query)
        items = [serialize_mongo_doc(item) for item in items]
        return {"items": items, "total": total, "page": page, "limit": limit}

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
    
    @staticmethod
    async def delete_article(slug: str):
        return await mongo.database.articles.update_one(
            {"slug": slug, "status": {"$ne": "deleted"}},
            {
                "$set": {
                    "status": "deleted",
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    @staticmethod
    async def list_articles(
    page: int = 1,
    limit: int = 10,
    domain_slug: str | None = None,
    status: str | None = None,
    search: str | None = None,
):
        query = {}

        if domain_slug:
            query["domain_slug"] = domain_slug

        if status:
            query["status"] = status

        if search:
            query["title"] = {"$regex": search, "$options": "i"}

        skip = (page - 1) * limit

        cursor = (
            mongo.database.articles
            .find(query)
            .sort("published_at", -1)
            .skip(skip)
            .limit(limit)
        )

        items = await cursor.to_list(length=limit)
        total = await mongo.database.articles.count_documents(query)

        # 🔥 Serialize Mongo docs
        items = [serialize_mongo_doc(item) for item in items]

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
        }
    

    
    @staticmethod
    async def get_article_stats():
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]

        results = await mongo.database.articles.aggregate(pipeline).to_list(length=None)

        stats = {
            "total": 0,
            "published": 0,
            "draft": 0,
            "deleted": 0,
            "trending": 0,
        }

        for item in results:
            status = item["_id"]
            count = item["count"]
            stats["total"] += count
            if status in stats:
                stats[status] = count

        stats["trending"] = await mongo.database.articles.count_documents({
            "is_trending": True,
            "status": "published"
        })

        return stats