import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from events_aggregator.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(500))
    place_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("places.id"),
    )
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    status: Mapped[str] = mapped_column(String(50))
    number_of_visitors: Mapped[int] = mapped_column(default=0)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    place: Mapped["Place"] = relationship(
        back_populates="events",
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="event",
    )