import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from events_aggregator.db.base import Base


class TicketIdempotency(Base):
    """ORM-модель для хранения результатов идемпотентных регистраций."""
    __tablename__ = "ticket_idempotency"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    seat: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
    )