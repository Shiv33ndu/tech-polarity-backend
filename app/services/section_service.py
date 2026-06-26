from app.db import mongo
from datetime import datetime
from zoneinfo import ZoneInfo

SECTION_COLLECTION = "sections"


class SectionService:

    @staticmethod
    async def get_active_sections():
        cursor = (
            mongo.database[SECTION_COLLECTION]
            .find({"is_active": True})
            .sort("order", 1)
        )
        return await cursor.to_list(length=None)

    @staticmethod
    async def get_all_sections():
        cursor = mongo.database[SECTION_COLLECTION].find().sort("order", 1)
        return await cursor.to_list(length=None)

    @staticmethod
    async def create_section(data: dict):
        data['created_at'] = datetime.now(ZoneInfo("Asia/Kolkata"))
        return await mongo.database[SECTION_COLLECTION].insert_one(data)

    @staticmethod
    async def update_section(slug: str, data: dict):
        return await mongo.database[SECTION_COLLECTION].update_one(
            {"slug": slug},
            {"$set": data}
        )

    @staticmethod
    async def delete_section(slug: str):
        return await mongo.database[SECTION_COLLECTION].delete_one(
            {"slug": slug}
        )

    @staticmethod
    async def section_exists(slug: str) -> bool:
        return (
            await mongo.database[SECTION_COLLECTION].count_documents({"slug": slug})
            > 0
        )
