import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from events_aggregator.db.base import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(500))
    seats_pattern: Mapped[str] = mapped_column(String(1000))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    events: Mapped[list["Event"]] = relationship(
        back_populates="place",
    )