from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.schemas.event import EventResponse


class EventsPaginator:
    def __init__(
        self,
        client: EventsProviderClient,
        changed_at: date,
    ) -> None:
        self.client = client
        self.changed_at = changed_at
        self.url: str | None = None
        self.events: list[EventResponse] = []
        self.finished = False

    def __aiter__(self) -> AsyncIterator[EventResponse]:
        return self

    async def __anext__(self) -> EventResponse:
        if self.events:
            return self.events.pop(0)

        if self.finished:
            raise StopAsyncIteration

        response = await self.client.events(
            changed_at=self.changed_at,
            url=self.url,
        )

        self.events = response.results
        self.url = response.next

        if self.url is None:
            self.finished = True

        if self.events:
            return self.events.pop(0)

        raise StopAsyncIteration