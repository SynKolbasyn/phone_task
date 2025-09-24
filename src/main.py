from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logging import setup_logging
from database.session import async_session
from models.call import Call, CallStatus
from models.record import Record
from worker.tasks import process_record_task


class CallCreate(BaseModel):
    caller: str
    receiver: str
    started_at: datetime | None = None


class CallResponse(BaseModel):
    id: UUID
    caller: str
    receiver: str
    started_at: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallWithRecordResponse(CallResponse):
    record: dict | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Set up logging on startup."""
    setup_logging()
    yield


app = FastAPI(
    title="Phone Task API",
    description="API for managing phone calls and audio recordings",
    version="1.0.0",
    lifespan=lifespan,
)


async def get_session() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/")
async def root() -> str:
    """Root endpoint."""
    return "Phone Task API is running!"


@app.post("/calls", response_model=CallResponse)
async def create_call(
    call_data: CallCreate,
    session: SessionDep,
) -> Call:
    """Create a new phone call."""
    call = Call(
        caller=call_data.caller,
        receiver=call_data.receiver,
        started_at=call_data.started_at or datetime.now(UTC),
        status=CallStatus.CREATED,
    )
    session.add(call)
    await session.commit()
    await session.refresh(call)
    return call


class CallListRequest(BaseModel):
    status: str | None = None
    caller: str | None = None
    receiver: str | None = None
    limit: int = 50
    offset: int = 0


@app.post("/calls/search", response_model=list[CallResponse])
async def list_calls(
    request: CallListRequest,
    session: SessionDep,
) -> list[Call]:
    """List phone calls with optional filtering."""
    query = select(Call)

    if request.status:
        query = query.where(Call.status == request.status)
    if request.caller:
        query = query.where(Call.caller.ilike(f"%{request.caller}%"))
    if request.receiver:
        query = query.where(Call.receiver.ilike(f"%{request.receiver}%"))

    query = (
        query.order_by(desc(Call.created_at))
        .offset(request.offset)
        .limit(request.limit)
    )
    result = await session.execute(query)
    return result.scalars().all()


@app.get("/calls", response_model=list[CallResponse])
async def get_recent_calls(
    session: SessionDep,
    limit: int = 10,
) -> list[Call]:
    """Get recent phone calls."""
    query = select(Call).order_by(desc(Call.created_at)).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@app.get("/calls/{call_id}", response_model=CallWithRecordResponse)
async def get_call(
    call_id: UUID,
    session: SessionDep,
) -> Call:
    """Get a specific phone call with its record."""
    query = select(Call).options(selectinload(Call.record)).where(Call.id == call_id)
    result = await session.execute(query)
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return call


@app.put("/calls/{call_id}/status")
async def update_call_status(
    call_id: UUID,
    status: str,
    session: SessionDep,
) -> dict:
    """Update call status."""
    call = await session.get(Call, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Validate status
    try:
        status_enum = CallStatus(status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}") from e

    call.status = status_enum
    await session.commit()

    return {"message": f"Call status updated to {status}"}


@app.post("/calls/{call_id}/record")
async def upload_record(
    call_id: UUID,
    session: SessionDep,
    file: Annotated[UploadFile, File()],
) -> dict:
    """Upload audio recording for a call."""
    call = await session.get(Call, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Check if call already has a record
    existing_record_query = select(Record).where(Record.call_id == call_id)
    existing_record_result = await session.execute(existing_record_query)
    if existing_record_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Call already has a record")

    # In production, this would upload to MinIO
    # For now, simulate with dummy data
    filename = file.filename or f"record_{call_id}.wav"
    object_path = f"/recordings/{call_id}/{filename}"

    # Create record entry
    record = Record(
        call_id=call_id,
        filename=filename,
        object_path=object_path,
        duration=60.0,  # Mock duration
        transcription="",  # Will be filled by processing task
    )
    session.add(record)

    # Update call status to processing
    call.status = CallStatus.PROCESSING

    await session.commit()
    await session.refresh(record)

    # Start background processing task
    process_record_task.delay(str(record.id))

    return {
        "message": "Record uploaded successfully",
        "record_id": record.id,
        "status": "processing",
    }


@app.get("/calls/{call_id}/record")
async def get_record(
    call_id: UUID,
    session: SessionDep,
) -> dict:
    """Get recording details for a call."""
    query = (
        select(Call)
        .options(selectinload(Call.record).selectinload(Record.silent_ranges))
        .where(Call.id == call_id)
    )
    result = await session.execute(query)
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    if not call.record:
        raise HTTPException(status_code=404, detail="No record found for this call")

    record = call.record
    silent_ranges = [
        {"start": sr.start, "end": sr.end, "duration": sr.end - sr.start}
        for sr in record.silent_ranges
    ]

    return {
        "record_id": record.id,
        "filename": record.filename,
        "duration": record.duration,
        "transcription": record.transcription,
        "silent_ranges": silent_ranges,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }
