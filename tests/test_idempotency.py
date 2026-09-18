from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from events_aggregator.core.enums import EventStatus
from events_aggregator.models.event import Event
from events_aggregator.models.ticket_idempotency import TicketIdempotency
from events_aggregator.schemas.seats import ProviderSeatsResponse
from events_aggregator.schemas.ticket import RegisterResponse
from events_aggregator.services.exceptions import IdempotencyConflictError


@pytest.mark.asyncio
async def test_register_success_with_idempotency(
    service,
    events,
    idempotency,
    client,
):
    """Проверяет успешную регистрацию с сохранением idempotency_key."""

    event_id = uuid4()
    ticket_id = uuid4()
    now = datetime.now(timezone.utc)
    idempotency_key = "test-idempotency-key"

    event = Event(
        id=event_id,
        name="Test Event",
        place_id=uuid4(),
        event_time=now + timedelta(days=1),
        registration_deadline=now + timedelta(hours=1),
        status=EventStatus.PUBLISHED,
        number_of_visitors=0,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )

    events.get.return_value = event
    client.seats.return_value = ProviderSeatsResponse(
        seats=["A1", "A2"],
    )
    client.register.return_value = RegisterResponse(
        ticket_id=ticket_id,
    )

    idempotency.get_key.return_value = None

    response = await service.register(
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        idempotency_key=idempotency_key,
    )

    assert response.ticket_id == ticket_id

    idempotency.get_key.assert_awaited_once_with(idempotency_key)
    idempotency.create.assert_awaited_once()

    created_idempotency = idempotency.create.await_args.args[0]

    assert created_idempotency.idempotency_key == idempotency_key
    assert created_idempotency.event_id == event_id
    assert created_idempotency.first_name == "Ivan"
    assert created_idempotency.last_name == "Ivanov"
    assert created_idempotency.email == "ivan@example.com"
    assert created_idempotency.seat == "A1"
    assert created_idempotency.ticket_id == ticket_id


@pytest.mark.asyncio
async def test_register_idempotency_repeat(
    service,
    idempotency,
    events,
    client,
    tickets,
    outbox,
):
    """Проверяет повторный запрос с тем же idempotency_key и данными"""

    event_id = uuid4()
    ticket_id = uuid4()
    idempotency_key = "test-idempotency-key"

    idempotency_record = TicketIdempotency(
        idempotency_key=idempotency_key,
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        ticket_id=ticket_id,
    )

    idempotency.get_key.return_value = idempotency_record

    response = await service.register(
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        idempotency_key=idempotency_key,
    )

    assert response.ticket_id == ticket_id

    idempotency.get_key.assert_awaited_once_with(idempotency_key)

    events.get.assert_not_awaited()
    client.seats.assert_not_awaited()
    client.register.assert_not_awaited()
    tickets.create.assert_not_awaited()
    outbox.create.assert_not_awaited()
    idempotency.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_idempotency_conflict(
    service,
    idempotency,
    events,
    client,
    tickets,
    outbox,
):
    """Проверяет конфликт при использовании idempotency_key с другими данными"""

    event_id = uuid4()
    ticket_id = uuid4()
    idempotency_key = "test-idempotency-key"

    idempotency_record = TicketIdempotency(
        idempotency_key=idempotency_key,
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        ticket_id=ticket_id,
    )

    idempotency.get_key.return_value = idempotency_record

    with pytest.raises(IdempotencyConflictError):
        await service.register(
            event_id=event_id,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A2",
            idempotency_key=idempotency_key,
        )

    idempotency.get_key.assert_awaited_once_with(idempotency_key)

    events.get.assert_not_awaited()
    client.seats.assert_not_awaited()
    client.register.assert_not_awaited()
    tickets.create.assert_not_awaited()
    outbox.create.assert_not_awaited()
    idempotency.create.assert_not_awaited()
