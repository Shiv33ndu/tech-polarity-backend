# app/db/mongo.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None
database = None


async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(settings.MONGO_URI)
    database = client[settings.MONGO_DB_NAME]

    # create indexes 
    await _create_indexes()


async def close_mongo_connection():
    global client
    if client:
        client.close()


async def _create_indexes():
    """
    Idempotent index creation.
    Safe to run on every startup.
    """

    # Categories
    await database.categories.create_index(
        [("slug", 1)], unique=True
    )
    await database.categories.create_index("is_active")
    await database.categories.create_index("order")

    # Articles
    await database.articles.create_index(
        [("slug", 1)], unique=True
    )
    await database.articles.create_index("domain_slug")
    await database.articles.create_index("is_trending")
    await database.articles.create_index("published_at")

    # Contacts
    await database.contacts.create_index("created_at")
    await database.contacts.create_index("email")
