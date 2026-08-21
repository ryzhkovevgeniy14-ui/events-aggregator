from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from events_aggregator.models.event import Event


class SqlAlchemyEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, event_id: UUID) -> Event | None:
        result = await self.session.execute(
            select(Event).where(Event.id == event_id),
        )

        return result.scalar_one_or_none()

    async def list(
        self,
        date_from: datetime | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Event], int]:
        query = select(Event)

        if date_from is not None:
            query = query.where(Event.event_time >= date_from)

        total_result = await self.session.execute(
            select(func.count()).select_from(query.subquery()),
        )
        total = total_result.scalar_one()

        query = (
            query
            .options(selectinload(Event.place))
            .order_by(Event.event_time)
        )

        offset = (page - 1) * page_size

        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)

        events = list(result.scalars().all())

        return events, total

    async def save(self, event: Event) -> None:
        self.session.add(event)
        await self.session.flush()