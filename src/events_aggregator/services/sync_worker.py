from __future__ import annotations

import asyncio

import httpx

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.core.logging import logger
from events_aggregator.db.session import async_session_maker
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


async def sync_worker(
    client: httpx.AsyncClient,
) -> None:
    while True:
        try:
            async with async_session_maker() as db:
                sync_service = SyncService(
                    client=EventsProviderClient(
                        base_url=settings.events_provider_base_url,
                        api_key=settings.events_provider_api_key,
                        client=client,
                    ),
                    events=SqlAlchemyEventRepository(db),
                    places=SqlAlchemyPlaceRepository(db),
                    sync_state=SqlAlchemySyncStateRepository(db),
                )

                await sync_service.sync()

        except asyncio.CancelledError:
            raise

        except Exception:  # noqa: BLE001
            logger.exception("Background synchronization failed")

        await asyncio.sleep(24 * 60 * 60)