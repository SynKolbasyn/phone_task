from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.record import Record


class SilentRange(Base):
    __tablename__ = "silent_ranges"

    record_id: Mapped[UUID] = mapped_column(
        ForeignKey("records.id", ondelete="CASCADE"),
    )
    start: Mapped[float] = mapped_column(nullable=False)
    end: Mapped[float] = mapped_column(nullable=False)

    record: Mapped[Record] = relationship(back_populates="silent_ranges")
