from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.core.enums import OutboxStatus
from events_aggregator.models.outbox import Outbox


class SqlAlchemyOutboxRepository:
    """SQLAlchemy-реализация репозитория Outbox."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, outbox: Outbox) -> None:
        self.session.add(outbox)
        await self.session.flush()

    async def get_pending(self, limit: int) -> list[Outbox]:
        result = await self.session.execute(
            select(Outbox)
            .where(Outbox.status == OutboxStatus.PENDING)
            .order_by(Outbox.created_at)
            .limit(limit),
        )

        return list(result.scalars().all())

    async def mark_as_sent(self, outbox: Outbox) -> None:
        outbox.status = OutboxStatus.SENT