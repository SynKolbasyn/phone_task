import asyncio
from asyncio import sleep
from uuid import UUID

from celery import Task
from pydub import AudioSegment

from config import Settings
from database.session import async_session
from models.record import Record
from models.silent_range import SilentRange
from worker.celery_app import app


def detect_silence(
    audio_segment: AudioSegment,
    min_silence_len: int = 1000,
    silence_thresh: int = -40,
) -> list[tuple[float, float]]:
    """Detect silent ranges in an audio segment."""
    silent_ranges = []

    # Process audio in chunks to find silent portions
    chunk_len = 100  # 100ms chunks
    silence_start = None

    for i in range(0, len(audio_segment), chunk_len):
        chunk = audio_segment[i:i + chunk_len]
        if len(chunk) < chunk_len:
            break

        # Check if chunk is silent (below threshold)
        if chunk.dBFS < silence_thresh:
            if silence_start is None:
                silence_start = i / 1000.0  # Convert to seconds
        # End of silence period
        elif silence_start is not None:
            silence_end = i / 1000.0
            silence_duration = (silence_end - silence_start) * 1000
            if silence_duration >= min_silence_len:
                silent_ranges.append((silence_start, silence_end))
            silence_start = None

    # Handle silence that extends to end of audio
    if silence_start is not None:
        silence_end = len(audio_segment) / 1000.0
        silence_duration = (silence_end - silence_start) * 1000
        if silence_duration >= min_silence_len:
            silent_ranges.append((silence_start, silence_end))

    return silent_ranges


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def process_record_task(_self: Task, record_id: str) -> None:
    """Process audio record - detect silence and update transcription."""
    Settings().logger.info(f"Starting processing for record ID: {record_id}")
    try:
        asyncio.run(process_record_async(record_id))
        Settings().logger.info(f"Finished processing for record ID: {record_id}")
    except Exception as e:
        Settings().logger.error(f"Error processing record {record_id}: {e}")
        raise


async def process_record_async(record_id: str) -> None:
    """Async function to process audio record."""
    async with async_session() as session:
        # Get the record
        record = await session.get(Record, UUID(record_id))
        if not record:
            msg = f"Record {record_id} not found"
            raise ValueError(msg)

        # Load audio file (in production, this would load from MinIO)
        # For now, simulate processing
        await sleep(2)  # Simulate audio loading time

        # Simulate audio segment for processing
        # In production: audio_segment = AudioSegment.from_file(record.object_path)
        # For now, create a dummy audio segment
        audio_segment = AudioSegment.silent(duration=record.duration * 1000)

        # Detect silent ranges
        silent_ranges = detect_silence(audio_segment)

        # Save silent ranges to database
        for start, end in silent_ranges:
            silent_range = SilentRange(
                record_id=record.id,
                start=start,
                end=end,
            )
            session.add(silent_range)

        # Update record with mock transcription
        record.transcription = "Processed transcription would go here"

        # Update call status to ready
        record.call.status = "ready"

        await session.commit()
