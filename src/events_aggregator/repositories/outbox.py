from __future__ import annotations

from typing import Protocol

from events_aggregator.models.outbox import Outbox


class OutboxRepository(Protocol):
    """Интерфейс репозитория для работы с событиями Outbox."""

    async def create(self, outbox: Outbox) -> None:
        ...

    async def get_pending(self, limit: int) -> list[Outbox]:
        ...

    async def mark_as_sent(self, outbox: Outbox) -> None:
        ...