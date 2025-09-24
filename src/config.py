from logging import Logger, getLogger
from os import environ
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent

    # Database configuration - use SQLite for testing
    database_url: str = environ.get(
        "DATABASE_URL", 
        f"sqlite+aiosqlite:///{Path(__file__).resolve().parent.parent}/phone_task.db"
    )
    
    # Redis configuration
    redis_url: str = environ.get(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # MinIO configuration
    minio_endpoint: str = environ.get("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key: str = environ.get("MINIO_ACCESS_KEY", "user")
    minio_secret_key: str = environ.get("MINIO_SECRET_KEY", "password")
    minio_bucket_name: str = environ.get("MINIO_BUCKET_NAME", "phone-records")

    logger: Logger = getLogger("fastapi")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
