from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from events_aggregator.models.event import Event


class EventRepository(Protocol):
    async def get(self, event_id: UUID) -> Event | None:
        ...

    async def list(
        self,
        date_from: datetime | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Event], int]:
        ...

    async def save(self, event: Event) -> None:
        ...