from asyncio import run, to_thread
from tempfile import NamedTemporaryFile, TemporaryDirectory
from uuid import UUID

from sqlalchemy import select

from config import Settings
from database.session import async_session
from models.call import CallStatus, Record, SilentRange
from utils.audio import process_audio
from utils.minio import download_file_from_minio
from worker.celery_app import app


async def process_audio_from_minio(record_id: UUID) -> None:
    async with async_session() as session:
        record = await session.scalar(select(Record).where(Record.id == record_id))
        if record is None:
            Settings().logger.error("Record not found: %s", record_id)
            return
        record.call.status = CallStatus.PROCESSING

    with TemporaryDirectory() as tmp_dir:
        with NamedTemporaryFile(dir=tmp_dir, delete=False) as file:
            file_path = file.name
        await to_thread(download_file_from_minio, record.object_path, file_path)
        duration, transcription, silent_ranges = await to_thread(
            process_audio,
            file_path,
        )

    async with async_session() as session:
        record = await session.scalar(select(Record).where(Record.id == record_id))
        if record is None:
            Settings().logger.error("Record not found: %s", record_id)
            return
        record.duration = duration
        record.transcription = transcription
        for start, end in silent_ranges:
            session.add(SilentRange(record_id=record_id, start=start, end=end))
        record.call.status = CallStatus.READY


@app.task
def process_record_task(record_id: UUID) -> None:
    run(process_audio_from_minio(record_id))
