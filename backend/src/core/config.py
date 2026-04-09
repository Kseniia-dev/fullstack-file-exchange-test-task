from functools import lru_cache
import os
from pathlib import Path


class Settings:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[2]
        self.storage_dir = self.base_dir / "storage" / "files"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.postgres_user = os.environ.get("POSTGRES_USER", "postgres")
        self.postgres_password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        self.postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
        self.postgres_port = os.environ.get("PGPORT", "5432")
        self.postgres_db = os.environ.get("POSTGRES_DB", "postgres")
        self.database_url = os.environ.get(
            "DATABASE_URL",
            (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            ),
        )
        self.redis_url = os.environ.get("REDIS_URL") or os.environ.get(
            "CELERY_BROKER_URL",
            "redis://backend-redis:6379/0",
        )
        self.cors_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
