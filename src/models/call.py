from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.record import Record


class CallStatus(Enum):
    CREATED = "created"
    PROCESSING = "processing" 
    READY = "ready"


class Call(Base):
    __tablename__ = "calls"

    caller: Mapped[str] = mapped_column(nullable=False, index=True)
    receiver: Mapped[str] = mapped_column(nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(CallStatus),
        default=CallStatus.CREATED,
        nullable=False,
        index=True,
    )

    record: Mapped[Record] = relationship(back_populates="call", uselist=False)
