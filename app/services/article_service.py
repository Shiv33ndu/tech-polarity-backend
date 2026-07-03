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
    async def get_related_articles(
        exclude_slug: str,
        domain_slug: str,
        section_slug: str,
        tags: list,
        limit: int,
    ):
        pipeline = [
            {
                "$match": {
                    "status": "published",
                    "slug": {"$ne": exclude_slug},
                }
            },
            {
                "$addFields": {
                    "relevance_score": {
                        "$add": [
                            # +3 per overlapping tag
                            {
                                "$multiply": [
                                    3,
                                    {
                                        "$size": {
                                            "$ifNull": [
                                                {
                                                    "$setIntersection": [
                                                        {"$ifNull": ["$tags", []]},
                                                        tags,
                                                    ]
                                                },
                                                [],
                                            ]
                                        }
                                    },
                                ]
                            },
                            # +2 for same sub-category
                            {"$cond": [{"$eq": ["$domain_slug", domain_slug]}, 2, 0]},
                            # +1 for same section/header
                            {"$cond": [{"$eq": ["$section_slug", section_slug]}, 1, 0]},
                        ]
                    }
                }
            },
            {"$match": {"relevance_score": {"$gt": 0}}},
            {"$sort": {"relevance_score": -1, "published_at": -1}},
            {"$limit": limit},
        ]

        results = await mongo.database[ARTICLE_COLLECTION].aggregate(pipeline).to_list(length=limit)

        # Fallback: if not enough results, fill with recent articles from same sub-category
        if len(results) < limit:
            existing_slugs = {r["slug"] for r in results} | {exclude_slug}
            fallback_cursor = (
                mongo.database[ARTICLE_COLLECTION]
                .find(
                    {
                        "status": "published",
                        "slug": {"$nin": list(existing_slugs)},
                        "domain_slug": domain_slug,
                    }
                )
                .sort("published_at", -1)
                .limit(limit - len(results))
            )
            results += await fallback_cursor.to_list(length=limit - len(results))

        return results

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

    # 🔹 Trending within a Section (across all its sub-categories)
    @staticmethod
    async def get_trending_by_section(section_slug: str, limit: int = 5):
        categories = await mongo.database[CATEGORY_COLLECTION].find(
            {"section_slug": section_slug, "is_active": True}
        ).to_list(length=None)
        domain_slugs = [c["slug"] for c in categories]

        if not domain_slugs:
            return []

        cursor = (
            mongo.database[ARTICLE_COLLECTION]
            .find(
                {
                    "domain_slug": {"$in": domain_slugs},
                    "is_trending": True,
                    "status": "published",
                }
            )
            .sort("published_at", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

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
            {"$match": {"status": "published"}},
            {
                "$addFields": {
                    "hours_since_publish": {
                        "$divide": [
                            {"$subtract": [now, "$published_at"]},
                            1000 * 60 * 60,
                        ]
                    }
                }
            },
            {
                "$addFields": {
                    "article_heat": {
                        "$add": [
                            {"$cond": ["$is_trending", 50, 0]},
                            {"$max": [0, {"$subtract": [50, "$hours_since_publish"]}]},
                        ]
                    }
                }
            },
            # Join to categories to get section_slug
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "domain_slug",
                    "foreignField": "slug",
                    "as": "category",
                }
            },
            {"$unwind": "$category"},
            {"$match": {"category.is_active": True, "category.section_slug": {"$ne": None}}},
            # Group by section
            {
                "$group": {
                    "_id": "$category.section_slug",
                    "total_heat": {"$sum": "$article_heat"},
                }
            },
            # Join to sections to get section name
            {
                "$lookup": {
                    "from": "sections",
                    "localField": "_id",
                    "foreignField": "slug",
                    "as": "section",
                }
            },
            {"$unwind": "$section"},
            {"$match": {"section.is_active": True}},
        ]

        data = await mongo.database.articles.aggregate(pipeline).to_list(length=None)

        if not data:
            return []

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

    @staticmethod
    async def get_articles_by_section(section_slug: str, page: int = 1, limit: int = 12):
        skip = (page - 1) * limit

        categories = await mongo.database[CATEGORY_COLLECTION].find(
            {"section_slug": section_slug, "is_active": True}
        ).to_list(length=None)
        domain_slugs = [c["slug"] for c in categories]

        if not domain_slugs:
            return {"items": [], "total": 0, "page": page, "limit": limit}

        query_filter = {
            "domain_slug": {"$in": domain_slugs},
            "status": "published",
        }
        cursor = (
            mongo.database[ARTICLE_COLLECTION]
            .find(query_filter)
            .sort("published_at", -1)
            .skip(skip)
            .limit(limit)
        )
        items = await cursor.to_list(length=limit)
        total = await mongo.database[ARTICLE_COLLECTION].count_documents(query_filter)
        items = [serialize_mongo_doc(item) for item in items]
        return {"items": items, "total": total, "page": page, "limit": limit}

    @staticmethod
    async def search_articles(query: str, page: int = 1, limit: int = 12):
        skip = (page - 1) * limit

        try:
            # Use MongoDB text index for relevance-ranked results across
            # title (weight 10), tags (5), description (3), content (1)
            mongo_query = {
                "status": "published",
                "$text": {"$search": query},
            }
            cursor = (
                mongo.database[ARTICLE_COLLECTION]
                .find(mongo_query, {"score": {"$meta": "textScore"}})
                .sort([("score", {"$meta": "textScore"}), ("published_at", -1)])
                .skip(skip)
                .limit(limit)
            )
            items = await cursor.to_list(length=limit)
            total = await mongo.database[ARTICLE_COLLECTION].count_documents(mongo_query)
        except Exception:
            # Fallback to regex search if text index is unavailable
            mongo_query = {
                "status": "published",
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"tags": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                ],
            }
            cursor = (
                mongo.database[ARTICLE_COLLECTION]
                .find(mongo_query)
                .sort("published_at", -1)
                .skip(skip)
                .limit(limit)
            )
            items = await cursor.to_list(length=limit)
            total = await mongo.database[ARTICLE_COLLECTION].count_documents(mongo_query)

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
        return await mongo.database.articles.delete_one({"slug": slug})
    
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