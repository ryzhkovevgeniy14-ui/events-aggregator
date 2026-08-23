from __future__ import annotations

from typing import Protocol
from uuid import UUID

from events_aggregator.models.ticket import Ticket


class TicketRepository(Protocol):
    """
    Интерфейс репозитория для работы с регистрациями на мероприятия.
    Определяет операции получения и создания регистрации.
    """
    async def get(self, ticket_id: UUID) -> Ticket | None:
        ...

    async def create(self, ticket: Ticket) -> None:
        ...