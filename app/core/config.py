from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Tech Polarity API"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str = "techpolaritydemo"

    # Admin Creds
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # Contact 
    RESEND_API_KEY: str
    CONTACT_TO_EMAIL: str

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:9002",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://admin-techpolarity.netlify.app",
        "https://tech-polarity-2026.vercel.app",
        "https://admin-techpolariy.vercel.app",
        "https://tech-polarity-2026-git-develop-tech-polarity.vercel.app",
        "https://tech-polarity-2026-roan.vercel.app",
        "https://admin-techpolariy-git-develop-tech-polarity.vercel.app",
        "https://admin-techpolariy-git-main-tech-polarity.vercel.app",
        "https://resplendent-axolotl-034f95.netlify.app",
        "https://www.techpolarity.com",
        "https://techpolarity.com",
        "https://admin.techpolarity.com",
    ]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()