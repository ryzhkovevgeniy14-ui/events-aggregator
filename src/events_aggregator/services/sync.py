from __future__ import annotations

from datetime import date, datetime, timezone

from events_aggregator.clients.events_paginator import EventsPaginator
from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.logging import logger
from events_aggregator.models.event import Event
from events_aggregator.models.place import Place
from events_aggregator.models.sync_state import SyncState
from events_aggregator.repositories.event import EventRepository
from events_aggregator.repositories.place import PlaceRepository
from events_aggregator.repositories.sync_state import SyncStateRepository
from events_aggregator.schemas.event import EventResponse
from events_aggregator.schemas.place import PlaceResponse


class SyncService:
    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
        places: PlaceRepository,
        sync_state: SyncStateRepository,
    ) -> None:
        self.client = client
        self.events = events
        self.places = places
        self.sync_state = sync_state

    async def sync(self) -> None:
        logger.info("Synchronization started")

        state = await self.sync_state.get()

        if state is None:
            state = SyncState(
                last_sync_time=None,
                last_changed_at=None,
                sync_status="running",
            )
            changed_at = date(2000, 1, 1)
            await self.sync_state.save(state)

            logger.info(
                "First synchronization started from %s",
                changed_at,
            )
        else:
            state.sync_status = "running"

            changed_at = (
                state.last_changed_at.date()
                if state.last_changed_at is not None
                else date(2000, 1, 1)
            )

            logger.info(
                "Incremental synchronization started from %s",
                changed_at,
            )

        paginator = EventsPaginator(
            client=self.client,
            changed_at=changed_at,
        )

        max_changed_at = state.last_changed_at
        synced_events = 0

        try:
            async for provider_event in paginator:
                await self._sync_place(provider_event.place)
                await self._sync_event(provider_event)

                synced_events += 1

                if (
                    max_changed_at is None
                    or provider_event.changed_at > max_changed_at
                ):
                    max_changed_at = provider_event.changed_at

            state.last_sync_time = datetime.now(timezone.utc)
            state.last_changed_at = max_changed_at
            state.sync_status = "success"

            await self.sync_state.save(state)

            logger.info(
                "Synchronization completed successfully. "
                "Events processed: %d",
                synced_events,
            )

        except Exception:
            state.sync_status = "failed"
            await self.sync_state.save(state)

            logger.exception(
                "Synchronization failed. Events processed: %d",
                synced_events,
            )

            raise

    async def _sync_place(
        self,
        provider_place: PlaceResponse
    ) -> Place:
        place = await self.places.get(provider_place.id)

        if place is None:
            place = Place(
                id=provider_place.id,
                name=provider_place.name,
                city=provider_place.city,
                address=provider_place.address,
                seats_pattern=provider_place.seats_pattern,
                changed_at=provider_place.changed_at,
                created_at=provider_place.created_at,
            )
            await self.places.save(place)

        else:
            place.name = provider_place.name
            place.city = provider_place.city
            place.address = provider_place.address
            place.seats_pattern = provider_place.seats_pattern
            place.changed_at = provider_place.changed_at
            place.created_at = provider_place.created_at

        return place

    async def _sync_event(
        self,
        provider_event: EventResponse,
    ) -> None:
        event = await self.events.get(provider_event.id)

        if event is None:
            event = Event(
                id=provider_event.id,
                name=provider_event.name,
                place_id=provider_event.place.id,
                event_time=provider_event.event_time,
                registration_deadline=provider_event.registration_deadline,
                status=provider_event.status,
                number_of_visitors=provider_event.number_of_visitors,
                changed_at=provider_event.changed_at,
                created_at=provider_event.created_at,
                status_changed_at=provider_event.status_changed_at,
            )
            await self.events.save(event)

        else:
            event.name = provider_event.name
            event.place_id = provider_event.place.id
            event.event_time = provider_event.event_time
            event.registration_deadline = provider_event.registration_deadline
            event.status = provider_event.status
            event.number_of_visitors = provider_event.number_of_visitors
            event.changed_at = provider_event.changed_at
            event.created_at = provider_event.created_at
            event.status_changed_at = provider_event.status_changed_at