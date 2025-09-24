from datetime import datetime

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
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
    status: Mapped[CallStatus] = mapped_column(
        default=CallStatus.CREATED,
        nullable=False,
        index=True,
    )

    record: Mapped[Record] = relationship(back_populates="call")
