from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from uuid import UUID

    from models.call import Call
    from models.silent_range import SilentRange


class Record(Base):
    __tablename__ = "records"

    call_id: Mapped[UUID] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(nullable=False)
    object_path: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[float] = mapped_column(nullable=False)
    transcription: Mapped[str] = mapped_column(nullable=False)

    call: Mapped[Call] = relationship(back_populates="record")
    silent_ranges: Mapped[list[SilentRange]] = relationship(back_populates="record")
