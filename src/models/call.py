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
from enum import StrEnum
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class CallStatus(StrEnum):
    CREATED = "created"
    PROCESSING = "processing"
    READY = "ready"


class Call(Base):
    __tablename__ = "calls"

    caller: Mapped[str] = mapped_column(nullable=False, index=True)
    receiver: Mapped[str] = mapped_column(nullable=False, index=True)
    started_at: Mapped[datetime]
    status: Mapped[CallStatus] = mapped_column(default=CallStatus.CREATED)

    record: Mapped["Record"] = relationship(
        back_populates="call",
        single_parent=True,
        lazy="joined",
    )


class SilentRange(Base):
    __tablename__ = "silent_ranges"

    record_id: Mapped[UUID] = mapped_column(
        ForeignKey("records.id", ondelete="CASCADE"),
    )
    start: Mapped[float]
    end: Mapped[float]

    record: Mapped["Record"] = relationship(
        back_populates="silent_ranges",
        lazy="joined",
    )


class Record(Base):
    __tablename__ = "records"

    call_id: Mapped[UUID] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"),
        unique=True,
    )
    filename: Mapped[str]
    object_path: Mapped[str]
    duration: Mapped[float]
    transcription: Mapped[str]
    presigned_url: Mapped[str]
    expires_at: Mapped[datetime]

    call: Mapped[Call] = relationship(
        back_populates="record",
        single_parent=True,
        lazy="joined",
    )
    silent_ranges: Mapped[list[SilentRange]] = relationship(
        back_populates="record",
        lazy="joined",
    )
