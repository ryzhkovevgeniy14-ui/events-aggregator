from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.repositories.event import EventRepository
from events_aggregator.schemas.seats import SeatsResponse


class EventNotFoundError(Exception):
    pass


class EventNotPublishedError(Exception):
    pass


class SeatsService:
    def __init__(
        self,
        events: EventRepository,
        client: EventsProviderClient,
        cache: dict[UUID, tuple[datetime, list[str]]]
    ) -> None:
        self.events = events
        self.client = client
        self.cache = cache

    async def get_seats(self, event_id: UUID) -> SeatsResponse:
        event = await self.events.get(event_id)

        if event is None:
            raise EventNotFoundError

        if event.status != "published":
            raise EventNotPublishedError

        cached = self.cache.get(event_id)

        if cached is not None:
            cached_at, seats = cached

            if (
                datetime.now(timezone.utc) - cached_at
                < timedelta(seconds=30)
            ):
                return SeatsResponse(
                    event_id=event_id,
                    available_seats=seats,
                )

        provider_response = await self.client.seats(event_id)

        seats = provider_response.seats

        self.cache[event_id] = (
            datetime.now(timezone.utc),
            seats,
        )

        return SeatsResponse(
            event_id=event_id,
            available_seats=seats,
        )