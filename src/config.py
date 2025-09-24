from logging import Logger, getLogger
from os import environ
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent

    database_url: str = environ["DATABASE_URL"]
    redis_url: str = environ["REDIS_URL"]

    minio_endpoint: str = environ["MINIO_ENDPOINT"]
    minio_access_key: str = environ["MINIO_ACCESS_KEY"]
    minio_secret_key: str = environ["MINIO_SECRET_KEY"]
    minio_bucket_name: str = environ["MINIO_BUCKET_NAME"]

    logger: Logger = getLogger("fastapi")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
