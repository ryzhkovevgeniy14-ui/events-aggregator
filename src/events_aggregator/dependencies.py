from __future__ import annotations

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.config import settings
from events_aggregator.db.depends import get_async_db
from events_aggregator.repositories.event_sqlalchemy import (
    SqlAlchemyEventRepository,
)
from events_aggregator.repositories.place_sqlalchemy import (
    SqlAlchemyPlaceRepository,
)
from events_aggregator.repositories.sync_state_sqlalchemy import (
    SqlAlchemySyncStateRepository,
)
from events_aggregator.services.sync import SyncService


async def get_http_client(
    request: Request,
) -> httpx.AsyncClient:
    return request.app.state.http_client


async def get_events_provider_client(
    client: httpx.AsyncClient = Depends(get_http_client),  # noqa: B008
) -> EventsProviderClient:
    return EventsProviderClient(
        base_url=settings.events_provider_base_url,
        api_key=settings.events_provider_api_key,
        client=client,
    )


async def get_sync_service(
    client: EventsProviderClient = Depends(get_events_provider_client),  # noqa: B008
    db: AsyncSession = Depends(get_async_db),  # noqa: B008
) -> SyncService:
    events = SqlAlchemyEventRepository(db)
    places = SqlAlchemyPlaceRepository(db)
    sync_state = SqlAlchemySyncStateRepository(db)

    return SyncService(
        client=client,
        events=events,
        places=places,
        sync_state=sync_state,
    )