from uuid import UUID

from pydantic import BaseModel


class SilentRangeSchema(BaseModel):
    start: float
    end: float

    model_config = {"from_attributes": True}


class RecordFullResponse(BaseModel):
    id: UUID
    call_id: UUID
    filename: str
    duration: float
    transcription: str
    silent_ranges: list[SilentRangeSchema]

    model_config = {"from_attributes": True}
