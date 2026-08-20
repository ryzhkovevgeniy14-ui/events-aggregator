from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.sync_state import SyncState


class SqlAlchemySyncStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> SyncState | None:
        result = await self.session.execute(
            select(SyncState),
        )

        return result.scalar_one_or_none()

    async def save(self, state: SyncState) -> None:
        self.session.add(state)
        await self.session.flush()