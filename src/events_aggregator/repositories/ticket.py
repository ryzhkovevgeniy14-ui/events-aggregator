from __future__ import annotations

from typing import Protocol
from uuid import UUID

from events_aggregator.models.ticket import Ticket


class TicketRepository(Protocol):
    async def get(self, ticket_id: UUID) -> Ticket | None:
        ...

    async def create(self, ticket: Ticket) -> None:
        ...