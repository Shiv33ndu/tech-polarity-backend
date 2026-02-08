from fastapi import APIRouter
from app.db import mongo

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    try:
        # Lightweight Mongo ping
        await mongo.database.command("ping")
        return {
            "status": "ok",
            "database": "connected",
        }
    except Exception:
        return {
            "status": "degraded",
            "database": "disconnected",
        }
