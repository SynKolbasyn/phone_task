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
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[CallStatus] = mapped_column(
        default=CallStatus.CREATED,
        nullable=False,
        index=True,
    )

    record: Mapped["Record"] = relationship(back_populates="call")


class SilentRange(Base):
    __tablename__ = "silent_ranges"

    record_id: Mapped[UUID] = mapped_column(
        ForeignKey("records.id", ondelete="CASCADE"),
    )
    start: Mapped[float] = mapped_column(nullable=False)
    end: Mapped[float] = mapped_column(nullable=False)

    record: Mapped["Record"] = relationship(back_populates="silent_ranges")


class Record(Base):
    __tablename__ = "records"

    call_id: Mapped[UUID] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(nullable=False)
    object_path: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[float] = mapped_column(nullable=False)
    transcription: Mapped[str] = mapped_column(nullable=False)

    call: Mapped[Call] = relationship(back_populates="record")
    silent_ranges: Mapped[list[SilentRange]] = relationship(back_populates="record")
