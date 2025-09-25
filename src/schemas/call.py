from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber


class CallCreate(BaseModel):
    caller: PhoneNumber
    receiver: PhoneNumber
    started_at: datetime


class CallResponse(BaseModel):
    id: UUID
    caller: PhoneNumber
    receiver: PhoneNumber
    started_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class SilentRange(BaseModel):
    start: float
    end: float

    model_config = ConfigDict(from_attributes=True)


class RecordingResponse(BaseModel):
    filename: str
    duration: float
    transcription: str
    silent_ranges: list[SilentRange]
    presigned_url: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CallFullResponse(CallResponse):
    record: RecordingResponse | None = None

    model_config = ConfigDict(from_attributes=True)
