from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError


class CallCreate(BaseModel):
    caller: str = Field(..., min_length=11, max_length=15)
    receiver: str = Field(..., min_length=11, max_length=15)
    started_at: datetime

    @field_validator("caller", "receiver")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not v.startswith("+7"):
            raise PydanticCustomError(
                "phone_number_format",
                "Phone number must start with '+7'",
                {"value": v},
            )
        if not v[2:].isdigit():
            raise PydanticCustomError(
                "phone_number_format",
                "Phone number must contain only digits after '+7'",
                {"value": v},
            )
        return v


class CallResponse(BaseModel):
    id: UUID
    caller: str
    receiver: str
    started_at: datetime
    status: str

    model_config = {"from_attributes": True}


class CallFullResponse(CallResponse):
    recording: "RecordingResponse | None" = None

    model_config = {"from_attributes": True}


class RecordingResponse(BaseModel):
    filename: str
    duration: float
    transcription: str
    presigned_url: str | None = None

    model_config = {"from_attributes": True}
