from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from events_aggregator.clients.events_paginator import EventsPaginator
from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.schemas.event import EventResponse, EventsResponse
from events_aggregator.schemas.place import PlaceResponse

CHANGED_AT = date(2000, 1, 1)


def create_event(event_id: str, name: str) -> EventResponse:
    """Создаёт тестовое событие."""
    return EventResponse(
        id=event_id,
        name=name,
        place=PlaceResponse(
            id="650e8400-e29b-41d4-a716-446655440001",
            name="Конференц-зал",
            city="Москва",
            address="ул. Ленина, д. 1",
            seats_pattern="A1-1000,B1-2000",
            changed_at=datetime.fromisoformat(
                "2026-01-01T10:00:00+03:00",
            ),
            created_at=datetime.fromisoformat(
                "2026-01-01T10:00:00+03:00",
            ),
        ),
        event_time=datetime.fromisoformat(
            "2026-01-11T17:00:00+03:00",
        ),
        registration_deadline=datetime.fromisoformat(
            "2026-01-10T17:00:00+03:00",
        ),
        status="published",
        number_of_visitors=5,
        changed_at=datetime.fromisoformat(
            "2026-01-04T22:28:35+03:00",
        ),
        created_at=datetime.fromisoformat(
            "2026-01-04T22:28:35+03:00",
        ),
        status_changed_at=datetime.fromisoformat(
            "2026-01-04T22:28:35+03:00",
        ),
    )


@pytest.fixture
def client() -> EventsProviderClient:
    """Создаёт мок Events Provider Client."""
    return AsyncMock(spec=EventsProviderClient)


@pytest.mark.asyncio
async def test_paginator_single_page(
    client: EventsProviderClient,
) -> None:
    """Проверяет получение событий с одной страницы."""
    event_1 = create_event(
        "550e8400-e29b-41d4-a716-446655440000",
        "Конференция по Python",
    )
    event_2 = create_event(
        "550e8400-e29b-41d4-a716-446655440002",
        "Конференция по FastAPI",
    )

    client.events.return_value = EventsResponse(
        next=None,
        previous=None,
        results=[event_1, event_2],
    )

    paginator = EventsPaginator(
        client=client,
        changed_at=CHANGED_AT,
    )

    events = [event async for event in paginator]

    assert events == [event_1, event_2]

    client.events.assert_awaited_once_with(
        changed_at=CHANGED_AT,
        url=None,
    )


@pytest.mark.asyncio
async def test_paginator_multiple_pages(
    client: EventsProviderClient,
) -> None:
    """Проверяет переход на следующую страницу по ссылке next."""
    event_1 = create_event(
        "550e8400-e29b-41d4-a716-446655440000",
        "Конференция по Python",
    )
    event_2 = create_event(
        "550e8400-e29b-41d4-a716-446655440002",
        "Конференция по FastAPI",
    )
    event_3 = create_event(
        "550e8400-e29b-41d4-a716-446655440003",
        "Конференция по PostgreSQL",
    )

    next_url = (
        "http://events-provider/api/events/"
        "?changed_at=2000-01-01&cursor=next"
    )

    client.events.side_effect = [
        EventsResponse(
            next=next_url,
            previous=None,
            results=[event_1, event_2],
        ),
        EventsResponse(
            next=None,
            previous=None,
            results=[event_3],
        ),
    ]

    paginator = EventsPaginator(
        client=client,
        changed_at=CHANGED_AT,
    )

    events = [event async for event in paginator]

    assert events == [event_1, event_2, event_3]

    assert client.events.await_count == 2

    client.events.assert_any_await(
        changed_at=CHANGED_AT,
        url=None,
    )

    client.events.assert_any_await(
        changed_at=CHANGED_AT,
        url=next_url,
    )


@pytest.mark.asyncio
async def test_paginator_empty_page(
    client: EventsProviderClient,
) -> None:
    """Проверяет завершение итерации при пустой странице."""
    client.events.return_value = EventsResponse(
        next=None,
        previous=None,
        results=[],
    )

    paginator = EventsPaginator(
        client=client,
        changed_at=CHANGED_AT,
    )

    events = [event async for event in paginator]

    assert events == []

    client.events.assert_awaited_once_with(
        changed_at=CHANGED_AT,
        url=None,
    )