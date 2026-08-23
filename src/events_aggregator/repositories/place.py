from __future__ import annotations

from typing import Protocol
from uuid import UUID

from events_aggregator.models.place import Place


class PlaceRepository(Protocol):
    """
    Интерфейс репозитория для работы с площадками.
    Определяет операции получения и сохранения площадок.
    """
    async def get(self, place_id: UUID) -> Place | None:
        ...

    async def save(self, place: Place) -> None:
        ...