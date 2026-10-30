import os
from typing import Optional
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=(".env", "../.env", "../../.env"),
            env_file_encoding="utf-8",
            extra="ignore"
        )
        PROJECT_NAME: str = Field(default="CitySense")
        ENV: str = Field(default="development")
        API_PORT: int = Field(default=8000)
        API_HOST: str = Field(default="0.0.0.0")

        DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./citysense.db")
        DATABASE_URL_SYNC: str = Field(default="sqlite:///./citysense.db")
        REDIS_URL: str = Field(default="redis://localhost:6379/0")

        STORAGE_BUCKET_NAME: str = Field(default="citysense-evidence")
        STORAGE_ACCESS_KEY: str = Field(default="mock-access-key")
        STORAGE_SECRET_KEY: str = Field(default="mock-secret-key")

        EMBEDDING_MODEL: str = Field(default="all-mpnet-base-v2")
        EMBEDDING_DIM: int = Field(default=768)
        LLM_PROVIDER: str = Field(default="mock_deterministic")
        LLM_API_KEY: Optional[str] = Field(default=None)

        JWT_SECRET: str = Field(default="citysense-dev-secret-key-change-in-production-98e508b3")
        TRACKING_SALT: str = Field(default="citysense-tracking-salt")

except (ImportError, Exception):
    # High-resilience fallback matching Pydantic specification
    class Settings:
        def __init__(self, **kwargs):
            self.PROJECT_NAME: str = kwargs.get("PROJECT_NAME", os.getenv("PROJECT_NAME", "CitySense"))
            self.ENV: str = kwargs.get("ENV", os.getenv("ENV", "development"))
            self.API_PORT: int = int(kwargs.get("API_PORT", os.getenv("API_PORT", "8000")))
            self.API_HOST: str = kwargs.get("API_HOST", os.getenv("API_HOST", "0.0.0.0"))

            self.DATABASE_URL: str = kwargs.get("DATABASE_URL", os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./citysense.db"))
            self.DATABASE_URL_SYNC: str = kwargs.get("DATABASE_URL_SYNC", os.getenv("DATABASE_URL_SYNC", "sqlite:///./citysense.db"))
            self.REDIS_URL: str = kwargs.get("REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))

            self.STORAGE_BUCKET_NAME: str = kwargs.get("STORAGE_BUCKET_NAME", os.getenv("STORAGE_BUCKET_NAME", "citysense-evidence"))
            self.STORAGE_ACCESS_KEY: str = kwargs.get("STORAGE_ACCESS_KEY", os.getenv("STORAGE_ACCESS_KEY", "mock-access-key"))
            self.STORAGE_SECRET_KEY: str = kwargs.get("STORAGE_SECRET_KEY", os.getenv("STORAGE_SECRET_KEY", "mock-secret-key"))

            self.EMBEDDING_MODEL: str = kwargs.get("EMBEDDING_MODEL", os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2"))
            self.EMBEDDING_DIM: int = int(kwargs.get("EMBEDDING_DIM", os.getenv("EMBEDDING_DIM", "768")))
            self.LLM_PROVIDER: str = kwargs.get("LLM_PROVIDER", os.getenv("LLM_PROVIDER", "mock_deterministic"))
            self.LLM_API_KEY: Optional[str] = kwargs.get("LLM_API_KEY", os.getenv("LLM_API_KEY", None))

            self.JWT_SECRET: str = kwargs.get("JWT_SECRET", os.getenv("JWT_SECRET", "citysense-dev-secret-key-change-in-production-98e508b3"))
            self.TRACKING_SALT: str = kwargs.get("TRACKING_SALT", os.getenv("TRACKING_SALT", "citysense-tracking-salt"))

settings = Settings()
