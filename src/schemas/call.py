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
