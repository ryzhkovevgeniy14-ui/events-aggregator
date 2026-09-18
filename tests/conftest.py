import os
from unittest.mock import AsyncMock

import pytest

os.environ.setdefault(
    "POSTGRES_CONNECTION_STRING",
    "postgresql+asyncpg://test:test@localhost:5432/test",
)
os.environ.setdefault("POSTGRES_DATABASE_NAME", "test")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_USERNAME", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault(
    "EVENTS_PROVIDER_BASE_URL",
    "http://events-provider",
)
os.environ.setdefault("EVENTS_PROVIDER_API_KEY", "test")
os.environ.setdefault(
    "CAPASHINO_BASE_URL",
    "http://capashino",
)
os.environ.setdefault("CAPASHINO_API_KEY", "test")
os.environ.setdefault("GLITCHTIP_DSN", "http://glitchtip")

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.repositories.event import EventRepository
from events_aggregator.repositories.outbox import OutboxRepository
from events_aggregator.repositories.ticket import TicketRepository
from events_aggregator.repositories.ticket_idempotency import (
    TicketIdempotencyRepository,
)
from events_aggregator.services.tickets import TicketService


@pytest.fixture
def events():
    return AsyncMock(spec=EventRepository)


@pytest.fixture
def tickets():
    return AsyncMock(spec=TicketRepository)


@pytest.fixture
def outbox():
    return AsyncMock(spec=OutboxRepository)


@pytest.fixture
def idempotency():
    return AsyncMock(spec=TicketIdempotencyRepository)


@pytest.fixture
def client():
    return AsyncMock(spec=EventsProviderClient)


@pytest.fixture
def service(events, tickets, outbox, idempotency, client):
    return TicketService(
        events=events,
        tickets=tickets,
        outbox=outbox,
        idempotency=idempotency,
        client=client,
    )
