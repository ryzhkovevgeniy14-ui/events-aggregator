from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from events_aggregator.db.base import Base


class SyncState(Base):
    __tablename__ = "sync_state"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        default=1,
    )
    last_sync_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    last_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    sync_status: Mapped[str] = mapped_column(
        String(50),
        default="never",
    )