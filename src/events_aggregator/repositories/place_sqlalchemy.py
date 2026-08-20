from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.place import Place


class SqlAlchemyPlaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, place_id: UUID) -> Place | None:
        result = await self.session.execute(
            select(Place).where(Place.id == place_id),
        )

        return result.scalar_one_or_none()

    async def save(self, place: Place) -> None:
        self.session.add(place)
        await self.session.flush()