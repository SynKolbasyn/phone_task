import asyncio
from asyncio import sleep

from config import Settings
from worker.celery_app import app


def detect_silence(audio_segment, min_silence_len: int = 1000, silence_thresh: int = -40) -> list[tuple[float, float]]:
    ...


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def process_record_task(record_id: str) -> None:
    Settings().logger.info(f"Starting processing for record ID: {record_id}")
    asyncio.run(process_record_async(record_id))
    Settings().logger.info(f"Finished processing for record ID: {record_id}")


async def process_record_async(record_id: str) -> None:
    await sleep(5)
