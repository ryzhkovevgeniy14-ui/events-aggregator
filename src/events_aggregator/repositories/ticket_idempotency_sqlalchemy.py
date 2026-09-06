from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.ticket_idempotency import TicketIdempotency


class SqlAlchemyTicketIdempotencyRepository:
    """SQLAlchemy-реализация репозитория idempotency."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_key(
        self,
        idempotency_key: str,
    ) -> TicketIdempotency | None:
        result = await self.session.execute(
            select(TicketIdempotency).where(
                TicketIdempotency.idempotency_key == idempotency_key,
            ),
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        idempotency: TicketIdempotency,
    ) -> None:
        self.session.add(idempotency)
        await self.session.flush()