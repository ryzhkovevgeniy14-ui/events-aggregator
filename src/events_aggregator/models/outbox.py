import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from events_aggregator.core.enums import OutboxStatus
from events_aggregator.db.base import Base


class Outbox(Base):
    """ORM-модель таблицы событий для отправки во внешние сервисы."""

    __tablename__ = "outbox"

    __table_args__ = (
        Index(
            "ix_outbox_status_created_at",
            "status",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[OutboxStatus] = mapped_column(
        String(50),
        default=OutboxStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )