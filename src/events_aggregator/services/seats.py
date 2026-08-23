from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.enums import EventStatus
from events_aggregator.repositories.event import EventRepository
from events_aggregator.schemas.seats import SeatsResponse
from events_aggregator.services.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
)


class SeatsService:
    """
    Сервис для получения свободных мест на мероприятии.

    Проверяет существование и статус мероприятия, использует
    кэширование списка мест на 30 секунд и при необходимости
    запрашивает актуальные данные у Events Provider API.
    """
    def __init__(
        self,
        events: EventRepository,
        client: EventsProviderClient,
        cache: dict[UUID, tuple[datetime, list[str]]],
    ) -> None:
        self.events = events
        self.client = client
        self.cache = cache

    async def get_seats(self, event_id: UUID) -> SeatsResponse:
        """
        Возвращает список свободных мест для указанного мероприятия.

        Данные берутся из кэша, если они были получены менее 30 секунд
        назад. Перед обращением к внешнему API проверяется существование
        мероприятия и его статус.
        """
        event = await self.events.get(event_id)

        if event is None:
            raise EventNotFoundError

        if event.status != EventStatus.PUBLISHED:
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