from celery import Celery

from config import Settings
from core.logging import setup_logging

setup_logging()

app = Celery(backend=Settings().redis_url, broker=Settings().redis_url, include="tasks")

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
