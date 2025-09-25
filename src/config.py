"""
Phone Call Service.

Copyright (C) 2025  Andrew Kozmin <syn.kolbasyn.06@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
