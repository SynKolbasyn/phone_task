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
