from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.db.mongo import connect_to_mongo, close_mongo_connection

# Routers (will be implemented next)
from app.api.v1 import articles_admin, home, navigation, auth, articles_public, contact, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager — replaces @app.on_event
    """
    # Setup
    setup_logging()
    print("🚀 STARTUP: Connecting to MongoDB")
    await connect_to_mongo()
    print("✅ MongoDB connected")
    yield
    # Teardown
    print("🛑 SHUTDOWN: Closing MongoDB")
    await close_mongo_connection()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan  # ⚡ New lifepath protocol
    )

    # Rate Limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API Routers
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
    app.include_router(home.router, prefix=settings.API_V1_PREFIX)
    app.include_router(articles_public.router, prefix=settings.API_V1_PREFIX)
    app.include_router(articles_admin.router, prefix=settings.API_V1_PREFIX)
    app.include_router(navigation.router, prefix=settings.API_V1_PREFIX)
    app.include_router(contact.router, prefix=settings.API_V1_PREFIX)
    app.include_router(health.router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
