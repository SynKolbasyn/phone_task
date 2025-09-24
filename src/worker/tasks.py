import asyncio
import tempfile
from pathlib import Path
from uuid import UUID

from minio import Minio

from config import Settings
from database.session import async_session
from models.call import Call, CallStatus, Record, SilentRange
from utils.audio import (
    detect_silence_ranges,
    generate_transcription,
    get_audio_duration,
)
from worker.celery_app import app


async def _process_record_async(record_id: UUID, settings: Settings) -> None:
    """Асинхронная функция для обработки записи."""
    async with async_session() as session:
        # 1. Получаем запись и связанный звонок
        record = await session.get(Record, record_id)
        if not record:
            settings.logger.error(f"Record with ID {record_id} not found.")
            return

        call = await session.get(Call, record.call_id)
        if not call:
            settings.logger.error(
                f"Call with ID {record.call_id} not found for record {record_id}.",
            )
            return

        # 2. Обновляем статус звонка на 'processing'
        call.status = CallStatus.PROCESSING
        await session.commit()
        settings.logger.info(f"Call {call.id} status updated to 'processing'.")

        # 3. Инициализируем MinIO клиент
        minio_client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,  # Внутри Docker сети HTTPS не используется
        )

        # 4. Скачиваем файл из MinIO во временный файл
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file_path = Path(tmp_file.name)
            try:
                minio_client.fget_object(
                    bucket_name=settings.minio_bucket_name,
                    object_name=record.object_path,
                    file_path=str(tmp_file_path),
                )
                settings.logger.info(
                    f"Downloaded {record.object_path} to {tmp_file_path}.",
                )

                # 5. Обрабатываем аудио
                duration = get_audio_duration(str(tmp_file_path))
                transcription = generate_transcription(str(tmp_file_path), duration)
                silent_ranges = detect_silence_ranges(str(tmp_file_path))

                # 6. Обновляем запись в БД
                record.duration = duration
                record.transcription = transcription

                # 7. Сохраняем диапазоны тишины
                # Сначала удалим старые, если они есть (на случай повторной обработки)
                await session.execute(
                    SilentRange.__table__.delete().where(
                        SilentRange.record_id == record.id,
                    ),
                )
                for start, end in silent_ranges:
                    silent_range = SilentRange(
                        record_id=record.id,
                        start=start,
                        end=end,
                    )
                    session.add(silent_range)

                # 8. Обновляем статус звонка на 'ready'
                call.status = CallStatus.READY
                await session.commit()
                settings.logger.info(
                    f"Processing for record {record_id} completed successfully.",
                )

            finally:
                # Удаляем временный файл
                tmp_file_path.unlink(missing_ok=True)


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def process_record_task(record_id: str) -> None:
    """Celery задача для обработки записи."""
    settings = Settings()
    settings.logger.info(f"Starting processing for record ID: {record_id}")
    try:
        # Конвертируем строку в UUID
        uuid_record_id = UUID(record_id)
        # Запускаем асинхронную обработку
        asyncio.run(_process_record_async(uuid_record_id, settings))
    except Exception as e:
        settings.logger.exception(f"Error processing record {record_id}: {e}")
        raise
    settings.logger.info(f"Finished processing for record ID: {record_id}")
