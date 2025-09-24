from celery import Celery

from config import Settings

app = Celery(
    broker=Settings().redis_url,
    backend=Settings().redis_url,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_pool="threads",
    worker_concurrency=2,
)
