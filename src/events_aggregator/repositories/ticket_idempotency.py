from __future__ import annotations

from typing import Protocol

from events_aggregator.models.ticket_idempotency import TicketIdempotency


class TicketIdempotencyRepository(Protocol):
    """Интерфейс репозитория для работы с idempotency-ключами."""

    async def get_key(
        self,
        idempotency_key: str,
    ) -> TicketIdempotency | None:
        ...

    async def create(
        self,
        idempotency: TicketIdempotency,
    ) -> None:
        ...