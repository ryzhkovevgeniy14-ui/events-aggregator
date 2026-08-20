from datetime import date
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from events_aggregator.clients.events_provider import EventsProviderClient


@pytest.fixture
def client() -> EventsProviderClient:
    """Создаёт клиент Events Provider с замоканным HTTP-клиентом."""
    http_client = AsyncMock(spec=httpx.AsyncClient)

    return EventsProviderClient(
        base_url="http://events-provider",
        api_key="test-api-key",
        client=http_client,
    )


@pytest.mark.asyncio
async def test_events_first_page(client: EventsProviderClient) -> None:
    """Проверяет получение первой страницы событий."""
    response = Mock()
    response.json.return_value = {
        "next": None,
        "previous": None,
        "results": [],
    }
    response.raise_for_status = Mock()

    client.client.get.return_value = response

    result = await client.events(date(2000, 1, 1))

    assert result.next is None
    assert result.previous is None
    assert result.results == []

    client.client.get.assert_awaited_once_with(
        "http://events-provider/api/events/",
        params={"changed_at": "2000-01-01"},
        headers={"x-api-key": "test-api-key"},
    )


@pytest.mark.asyncio
async def test_events_next_page(client: EventsProviderClient) -> None:
    """Проверяет получение следующей страницы событий по URL."""
    response = Mock()
    response.json.return_value = {
        "next": None,
        "previous": "http://events-provider/api/events/?cursor=previous",
        "results": [],
    }
    response.raise_for_status = Mock()

    client.client.get.return_value = response

    next_url = "http://events-provider/api/events/?cursor=next"

    result = await client.events(
        date(2000, 1, 1),
        url=next_url,
    )

    assert result.previous == (
        "http://events-provider/api/events/?cursor=previous"
    )

    client.client.get.assert_awaited_once_with(
        next_url,
        headers={"x-api-key": "test-api-key"},
    )


@pytest.mark.asyncio
async def test_seats(client: EventsProviderClient) -> None:
    """Проверяет получение списка свободных мест."""
    event_id = "550e8400-e29b-41d4-a716-446655440000"

    response = Mock()
    response.json.return_value = {
        "event_id": event_id,
        "available_seats": ["A1", "A2"],
    }
    response.raise_for_status = Mock()

    client.client.get.return_value = response

    result = await client.seats(event_id)

    assert result.available_seats == ["A1", "A2"]

    client.client.get.assert_awaited_once_with(
        f"http://events-provider/api/events/{event_id}/seats/",
        headers={"x-api-key": "test-api-key"},
    )


@pytest.mark.asyncio
async def test_register(client: EventsProviderClient) -> None:
    """Проверяет регистрацию участника на мероприятие."""
    event_id = "550e8400-e29b-41d4-a716-446655440000"
    ticket_id = "1fed0122-b675-42e2-8ae7-49bfb53e8d7f"

    response = Mock()
    response.json.return_value = {
        "ticket_id": ticket_id,
    }
    response.raise_for_status = Mock()

    client.client.post.return_value = response

    result = await client.register(
        event_id=event_id,
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        seat="A15",
    )

    assert str(result.ticket_id) == ticket_id

    client.client.post.assert_awaited_once_with(
        f"http://events-provider/api/events/{event_id}/register/",
        headers={"x-api-key": "test-api-key"},
        json={
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "seat": "A15",
        },
    )


@pytest.mark.asyncio
async def test_unregister(client: EventsProviderClient) -> None:
    """Проверяет отмену регистрации участника."""
    event_id = "550e8400-e29b-41d4-a716-446655440000"
    ticket_id = "1fed0122-b675-42e2-8ae7-49bfb53e8d7f"

    response = Mock()
    response.json.return_value = {
        "success": True,
    }
    response.raise_for_status = Mock()

    client.client.request.return_value = response

    result = await client.unregister(
        event_id=event_id,
        ticket_id=ticket_id,
    )

    assert result.success is True

    client.client.request.assert_awaited_once_with(
        "DELETE",
        f"http://events-provider/api/events/{event_id}/unregister/",
        headers={"x-api-key": "test-api-key"},
        json={"ticket_id": ticket_id},
    )