from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from events_aggregator.core.enums import EventStatus, TicketStatus
from events_aggregator.models.event import Event
from events_aggregator.models.ticket import Ticket
from events_aggregator.schemas.seats import ProviderSeatsResponse
from events_aggregator.schemas.ticket import RegisterResponse, UnregisterResponse
from events_aggregator.services.exceptions import (
    EventAlreadyPassedError,
    EventNotFoundError,
    EventNotPublishedError,
    RegistrationDeadlinePassedError,
    SeatNotAvailableError,
    TicketNotFoundError,
)


@pytest.mark.asyncio
async def test_register_success(
    service,
    events,
    tickets,
    outbox,
    idempotency,
    client,
):
    """Проверяет успешную регистрацию и создание Ticket и Outbox"""

    event_id = uuid4()
    ticket_id = uuid4()
    now = datetime.now(timezone.utc)

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

    response = await service.register(
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
    )

    assert response.ticket_id == ticket_id

    events.get.assert_awaited_once_with(event_id)

    client.seats.assert_awaited_once_with(event_id)

    client.register.assert_awaited_once_with(
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
    )

    tickets.create.assert_awaited_once()
    ticket = tickets.create.await_args.args[0]

    assert ticket.ticket_id == ticket_id
    assert ticket.event_id == event_id
    assert ticket.first_name == "Ivan"
    assert ticket.last_name == "Ivanov"
    assert ticket.email == "ivan@example.com"
    assert ticket.seat == "A1"
    assert ticket.status == TicketStatus.ACTIVE

    outbox.create.assert_awaited_once()
    created_outbox = outbox.create.await_args.args[0]

    assert created_outbox.event_type == "ticket_purchased"
    assert created_outbox.payload["ticket_id"] == str(ticket_id)
    assert created_outbox.payload["event_name"] == "Test Event"

    idempotency.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_event_not_found(
    service,
    events,
    client,
    tickets,
    outbox,
    idempotency,
):
    """Проверяет ошибку при отсутствии мероприятия"""

    event_id = uuid4()

    events.get.return_value = None

    with pytest.raises(EventNotFoundError):
        await service.register(
            event_id=event_id,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A1",
        )

    events.get.assert_awaited_once_with(event_id)

    client.seats.assert_not_awaited()
    client.register.assert_not_awaited()
    tickets.create.assert_not_awaited()
    outbox.create.assert_not_awaited()
    idempotency.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_event_not_published(
    service,
    events,
    client,
    tickets,
    outbox,
    idempotency,
):
    """Проверяет ошибку при регистрации на неопубликованное мероприятие"""

    event_id = uuid4()
    now = datetime.now(timezone.utc)

    event = Event(
        id=event_id,
        name="Test Event",
        place_id=uuid4(),
        event_time=now + timedelta(days=1),
        registration_deadline=now + timedelta(hours=1),
        status=EventStatus.NEW,
        number_of_visitors=0,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )

    events.get.return_value = event

    with pytest.raises(EventNotPublishedError):
        await service.register(
            event_id=event_id,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A1",
        )

    events.get.assert_awaited_once_with(event_id)

    client.seats.assert_not_awaited()
    client.register.assert_not_awaited()
    tickets.create.assert_not_awaited()
    outbox.create.assert_not_awaited()
    idempotency.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_deadline_passed(
    service,
    events,
    client,
    tickets,
    outbox,
    idempotency,
):
    """Проверяет ошибку при истёкшем дедлайне регистрации"""

    event_id = uuid4()
    now = datetime.now(timezone.utc)

    event = Event(
        id=event_id,
        name="Test Event",
        place_id=uuid4(),
        event_time=now + timedelta(days=1),
        registration_deadline=now - timedelta(hours=1),
        status=EventStatus.PUBLISHED,
        number_of_visitors=0,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )

    events.get.return_value = event

    with pytest.raises(RegistrationDeadlinePassedError):
        await service.register(
            event_id=event_id,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A1",
        )

    events.get.assert_awaited_once_with(event_id)

    client.seats.assert_not_awaited()
    client.register.assert_not_awaited()
    tickets.create.assert_not_awaited()
    outbox.create.assert_not_awaited()
    idempotency.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_seat_not_available(
    service,
    events,
    client,
    tickets,
    outbox,
    idempotency,
):
    """Проверяет ошибку при выборе недоступного места"""

    event_id = uuid4()
    now = datetime.now(timezone.utc)

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

    with pytest.raises(SeatNotAvailableError):
        await service.register(
            event_id=event_id,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="B1",
        )

    events.get.assert_awaited_once_with(event_id)
    client.seats.assert_awaited_once_with(event_id)

    client.register.assert_not_awaited()
    tickets.create.assert_not_awaited()
    outbox.create.assert_not_awaited()
    idempotency.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_provider_seat_error(
    service,
    events,
    client,
    tickets,
    outbox,
    idempotency,
):
    """Проверяет ошибку при отказе Events Provider зарегистрировать место"""

    event_id = uuid4()
    now = datetime.now(timezone.utc)

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

    client.register.side_effect = SeatNotAvailableError(
        "Seat is not available",
    )

    with pytest.raises(SeatNotAvailableError):
        await service.register(
            event_id=event_id,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A1",
        )

    events.get.assert_awaited_once_with(event_id)
    client.seats.assert_awaited_once_with(event_id)
    client.register.assert_awaited_once_with(
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
    )

    tickets.create.assert_not_awaited()
    outbox.create.assert_not_awaited()
    idempotency.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_unregister_success(
    service,
    events,
    tickets,
    client,
):
    """Проверяет успешную отмену регистрации"""

    ticket_id = uuid4()
    event_id = uuid4()
    now = datetime.now(timezone.utc)

    ticket = Ticket(
        ticket_id=ticket_id,
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        status=TicketStatus.ACTIVE,
    )

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

    tickets.get.return_value = ticket
    events.get.return_value = event

    client.unregister.return_value = UnregisterResponse(success=True)
    response = await service.unregister(ticket_id)

    assert response.success is True
    assert ticket.status == TicketStatus.CANCELLED

    tickets.get.assert_awaited_once_with(ticket_id)
    events.get.assert_awaited_once_with(event_id)

    client.unregister.assert_awaited_once_with(
        event_id=event_id,
        ticket_id=ticket_id,
    )


@pytest.mark.asyncio
async def test_unregister_ticket_not_found(
    service,
    tickets,
    events,
    client,
):
    """Проверяет ошибку при отмене несуществующего билета"""

    ticket_id = uuid4()

    tickets.get.return_value = None

    with pytest.raises(TicketNotFoundError):
        await service.unregister(ticket_id)

    tickets.get.assert_awaited_once_with(ticket_id)

    events.get.assert_not_awaited()
    client.unregister.assert_not_awaited()


@pytest.mark.asyncio
async def test_unregister_event_not_found(
    service,
    tickets,
    events,
    client,
):
    """Проверяет ошибку при отсутствии мероприятия, связанного с билетом"""

    ticket_id = uuid4()
    event_id = uuid4()

    ticket = Ticket(
        ticket_id=ticket_id,
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        status=TicketStatus.ACTIVE,
    )

    tickets.get.return_value = ticket
    events.get.return_value = None

    with pytest.raises(EventNotFoundError):
        await service.unregister(ticket_id)

    tickets.get.assert_awaited_once_with(ticket_id)
    events.get.assert_awaited_once_with(event_id)

    client.unregister.assert_not_awaited()


@pytest.mark.asyncio
async def test_unregister_event_already_passed(
    service,
    tickets,
    events,
    client,
):
    """Проверяет запрет отмены после начала мероприятия"""

    ticket_id = uuid4()
    event_id = uuid4()
    now = datetime.now(timezone.utc)

    ticket = Ticket(
        ticket_id=ticket_id,
        event_id=event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        status=TicketStatus.ACTIVE,
    )

    event = Event(
        id=event_id,
        name="Test Event",
        place_id=uuid4(),
        event_time=now - timedelta(hours=1),
        registration_deadline=now - timedelta(days=1),
        status=EventStatus.PUBLISHED,
        number_of_visitors=0,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )

    tickets.get.return_value = ticket
    events.get.return_value = event

    with pytest.raises(EventAlreadyPassedError):
        await service.unregister(ticket_id)

    tickets.get.assert_awaited_once_with(ticket_id)
    events.get.assert_awaited_once_with(event_id)

    client.unregister.assert_not_awaited()

    assert ticket.status == TicketStatus.ACTIVE
