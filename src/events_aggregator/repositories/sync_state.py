from __future__ import annotations

from typing import Protocol

from events_aggregator.models.sync_state import SyncState


class SyncStateRepository(Protocol):
    """
    Интерфейс репозитория для работы с состоянием синхронизации.
    Определяет операции получения и сохранения состояния синхронизации.
    """
    async def get(self) -> SyncState | None:
        ...

    async def save(self, state: SyncState) -> None:
        ...