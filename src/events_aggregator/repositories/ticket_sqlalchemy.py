from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.ticket import Ticket


class SqlAlchemyTicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, ticket_id: UUID) -> Ticket | None:
        result = await self.session.execute(
            select(Ticket).where(Ticket.ticket_id == ticket_id),
        )

        return result.scalar_one_or_none()

    async def create(self, ticket: Ticket) -> None:
        self.session.add(ticket)
        await self.session.flush()