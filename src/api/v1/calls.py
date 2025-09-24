import uuid
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import async_session
from config import Settings
from models.call import Call, Record
from schemas.call import CallCreate, CallFullResponse
from worker.tasks import process_record_task

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/", response_model=CallCreate, status_code=status.HTTP_201_CREATED)
async def create_call(
    call_data: CallCreate,
    session: Annotated[AsyncSession, Depends(async_session)],
) -> Call:
    """Создает новый звонок."""
    new_call = Call(**call_data.model_dump())
    session.add(new_call)
    await session.commit()
    await session.refresh(new_call)
    return new_call


@router.post("/{call_id}/recording/", status_code=status.HTTP_201_CREATED)
async def upload_recording(
    call_id: uuid.UUID,
    file: UploadFile,
    session: Annotated[AsyncSession, Depends(async_session)],
) -> dict[str, str]:
    """Загружает аудиофайл записи звонка."""
    # 1. Проверяем существование звонка
    call = await session.get(Call, call_id)
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found",
        )

    # 2. Генерируем уникальное имя файла
    file_extension = Path(file.filename or "recording").suffix
    object_name = f"calls/{call_id}/{uuid.uuid4()}{file_extension}"

    # 3. Загружаем файл в MinIO
    settings = Settings()
    minio_client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )

    # Убедимся, что бакет существует
    if not minio_client.bucket_exists(settings.minio_bucket_name):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MinIO bucket does not exist",
        )

    # Читаем содержимое файла
    file_content = await file.read()
    file_stream = BytesIO(file_content)
    file_size = len(file_content)

    try:
        minio_client.put_object(
            bucket_name=settings.minio_bucket_name,
            object_name=object_name,
            data=file_stream,
            length=file_size,
            content_type=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        Settings().logger.exception(f"Error uploading file to MinIO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage",
        ) from e

    # 4. Создаем запись в БД
    new_record = Record(
        call_id=call_id,
        filename=file.filename or "unknown",
        object_path=object_name,
        duration=0.0,  # Будет обновлено позже
        transcription="",  # Будет обновлено позже
    )
    session.add(new_record)
    await session.commit()

    # 5. Запускаем фоновую задачу обработки
    process_record_task.delay(str(new_record.id))

    return {"message": "File uploaded successfully", "object_name": object_name}


@router.get("/{call_id}/", response_model=CallFullResponse)
async def get_call(
    call_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(async_session)],
) -> Call:
    """Возвращает информацию о звонке, включая запись."""
    call = await session.get(Call, call_id)
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found",
        )

    # Если запись существует и статус 'ready', генерируем presigned URL
    if call.record and call.status == "ready":
        settings = Settings()
        minio_client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        try:
            presigned_url = minio_client.presigned_get_object(
                bucket_name=settings.minio_bucket_name,
                object_name=call.record.object_path,
                expires=3600,  # URL действителен 1 час
            )
            # Добавляем URL в объект записи для Pydantic
            call.record.presigned_url = presigned_url
        except Exception as e:
            Settings().logger.warning(f"Could not generate presigned URL: {e}")

    return call
