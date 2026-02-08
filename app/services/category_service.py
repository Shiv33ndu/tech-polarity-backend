from app.db import mongo
from datetime import datetime
from zoneinfo import ZoneInfo

CATEGORY_COLLECTION = "categories"


class CategoryService:

    @staticmethod
    async def get_active_categories():
        cursor = (
            mongo.database[CATEGORY_COLLECTION]
            .find({"is_active": True})
            .sort("order", 1)
        )
        return await cursor.to_list(length=None)

    @staticmethod
    async def get_all_categories():
        cursor = mongo.database[CATEGORY_COLLECTION].find().sort("order", 1)
        return await cursor.to_list(length=None)

    @staticmethod
    async def create_category(data: dict):
        data['created_at'] = datetime.now(ZoneInfo("Asia/Kolkata"))
        return await mongo.database[CATEGORY_COLLECTION].insert_one(data)

    @staticmethod
    async def update_category(slug: str, data: dict):
        return await mongo.database[CATEGORY_COLLECTION].update_one(
            {"slug": slug},
            {"$set": data}
        )

    @staticmethod
    async def delete_category(slug: str):
        return await mongo.database[CATEGORY_COLLECTION].delete_one(
            {"slug": slug}
        )

    @staticmethod
    async def category_exists(slug: str) -> bool:
        return (
            await mongo.database[CATEGORY_COLLECTION].count_documents({"slug": slug})
            > 0
        )
