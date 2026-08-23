import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from events_aggregator.core.enums import TicketStatus
from events_aggregator.db.base import Base

if TYPE_CHECKING:
    from events_aggregator.models.event import Event


class Ticket(Base):
    """ORM-модель таблицы регистраций участников на мероприятия."""
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column()
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id"),
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    seat: Mapped[str] = mapped_column(String(50))
    status: Mapped[TicketStatus] = mapped_column(
        String(50),
        default=TicketStatus.ACTIVE,
    )

    event: Mapped["Event"] = relationship(
        back_populates="tickets",
    )