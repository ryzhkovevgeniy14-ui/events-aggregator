from __future__ import annotations

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.db.depends import get_async_db
from events_aggregator.repositories.event import EventRepository
from events_aggregator.repositories.event_sqlalchemy import (
    SqlAlchemyEventRepository,
)
from events_aggregator.repositories.place_sqlalchemy import (
    SqlAlchemyPlaceRepository,
)
from events_aggregator.repositories.sync_state_sqlalchemy import (
    SqlAlchemySyncStateRepository,
)
from events_aggregator.repositories.ticket import TicketRepository
from events_aggregator.repositories.ticket_sqlalchemy import (
    SqlAlchemyTicketRepository,
)
from events_aggregator.services.seats import SeatsService
from events_aggregator.services.sync import SyncService
from events_aggregator.services.tickets import TicketService


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


async def get_event_repository(
    db: AsyncSession = Depends(get_async_db),  # noqa: B008
) -> SqlAlchemyEventRepository:
    return SqlAlchemyEventRepository(db)


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


async def get_seats_service(
    request: Request,
    events: EventRepository = Depends(get_event_repository),  # noqa: B008
    client: EventsProviderClient = Depends(get_events_provider_client),  # noqa: B008
) -> SeatsService:
    return SeatsService(
        events=events,
        client=client,
        cache=request.app.state.seats_cache,
    )


async def get_ticket_service(
    events: EventRepository = Depends(get_event_repository),  # noqa: B008
    db: AsyncSession = Depends(get_async_db),  # noqa: B008
    client: EventsProviderClient = Depends(get_events_provider_client),  # noqa: B008
) -> TicketService:
    tickets: TicketRepository = SqlAlchemyTicketRepository(db)

    return TicketService(
        events=events,
        tickets=tickets,
        client=client,
    )