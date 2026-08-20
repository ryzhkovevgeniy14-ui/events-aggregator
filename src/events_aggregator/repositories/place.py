from __future__ import annotations

from typing import Protocol
from uuid import UUID

from events_aggregator.models.place import Place


class PlaceRepository(Protocol):
    async def get(self, place_id: UUID) -> Place | None:
        ...

    async def save(self, place: Place) -> None:
        ...