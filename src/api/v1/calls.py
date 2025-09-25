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


from asyncio import to_thread
from datetime import UTC, datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from minio import Minio
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from database.session import provide_async_session
from models.call import Call, Record
from schemas.call import CallCreate, CallFullResponse
from worker.tasks import process_record_task

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/calls/", status_code=status.HTTP_201_CREATED)
async def create_call(
    call_data: CallCreate,
    session: Annotated[AsyncSession, Depends(provide_async_session)],
) -> UUID:
    call_data.started_at = call_data.started_at.replace(tzinfo=None)
    new_call = Call(**call_data.model_dump())
    session.add(new_call)
    await session.flush()
    Settings().logger.info("%s", new_call)
    return new_call.id


def save_to_minio(file: bytes, file_name: str) -> None:
    minio_client = Minio(
        Settings().minio_endpoint,
        access_key=Settings().minio_access_key,
        secret_key=Settings().minio_secret_key,
        secure=True,
        cert_check=False,
    )

    if not minio_client.bucket_exists(Settings().minio_bucket_name):
        minio_client.make_bucket(Settings().minio_bucket_name)

    try:
        minio_client.put_object(
            bucket_name=Settings().minio_bucket_name,
            object_name=file_name,
            data=BytesIO(file),
            length=len(file),
        )
    except Exception as e:
        Settings().logger.exception(f"Error uploading file to MinIO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage",
        ) from e


@router.post("/calls/{call_id}/recording/", status_code=status.HTTP_201_CREATED)
async def upload_recording(
    call_id: UUID,
    file: UploadFile,
    session: Annotated[AsyncSession, Depends(provide_async_session)],
) -> Response:
    call = await session.get(Call, call_id)
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found",
        )

    file_extension = Path(file.filename or "recording").suffix
    file_name = f"calls/{call_id}/{uuid4()}{file_extension}"

    await to_thread(save_to_minio, await file.read(), file_name)

    new_record = Record(
        call_id=call_id,
        filename=file.filename or "unknown",
        object_path=file_name,
        duration=0.0,
        transcription="",
        presigned_url="",
        expires_at=datetime.now(UTC).replace(tzinfo=None),
    )
    session.add(new_record)
    try:
        await session.flush()
    except IntegrityError as error:
        Settings().logger.info("unique constraint failed: %s", error)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate recording",
        ) from error

    process_record_task.delay(new_record.id)
    return Response(status_code=status.HTTP_201_CREATED)


def get_call_with_record(call: Call) -> Call:
    if call.record is None:
        return call

    if call.record.expires_at >= datetime.now(UTC).replace(tzinfo=None):
        return call

    minio_client = Minio(
        Settings().minio_endpoint,
        access_key=Settings().minio_access_key,
        secret_key=Settings().minio_secret_key,
        secure=True,
        cert_check=False,
    )
    call.record.presigned_url = minio_client.presigned_get_object(
        bucket_name=Settings().minio_bucket_name,
        object_name=call.record.object_path,
        expires=timedelta(hours=1),
    )
    call.record.expires_at = (datetime.now(UTC) + timedelta(hours=1)).replace(
        tzinfo=None,
    )

    return call


@router.get("/find/", response_model=list[CallFullResponse])
async def find_call(
    phone_number: PhoneNumber,
    session: Annotated[AsyncSession, Depends(provide_async_session)],
) -> list[Call]:
    calls = await session.scalars(
        select(Call).where(
            (Call.caller == phone_number) | (Call.receiver == phone_number),
        ),
    )
    return [await to_thread(get_call_with_record, call) for call in calls.unique()]


@router.get("/{call_id}/", response_model=CallFullResponse)
async def get_call(
    call_id: UUID,
    session: Annotated[AsyncSession, Depends(provide_async_session)],
) -> Call:
    call = await session.scalar(select(Call).where(Call.id == call_id))
    if call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found",
        )

    return get_call_with_record(call)
