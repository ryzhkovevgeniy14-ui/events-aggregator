import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from events_aggregator.core.enums import OutboxStatus
from events_aggregator.models.outbox import Outbox
from events_aggregator.services.outbox_worker import outbox_worker


class StopWorker(Exception):
    pass


@pytest.mark.asyncio
async def test_send_success():
    """Проверяет успешную отправку уведомления и изменение статуса события"""

    ticket_id = uuid.uuid4()

    outbox = Outbox(
        event_type="ticket_purchased",
        payload={
            "ticket_id": str(ticket_id),
            "event_name": "Python Meetup",
        },
        status=OutboxStatus.PENDING,
    )

    client = AsyncMock()
    session = AsyncMock()

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=session)

    repository = MagicMock()
    repository.get_pending = AsyncMock(return_value=[outbox])

    with (
        patch(
            "events_aggregator.services.outbox_worker.async_session_maker",
            return_value=session_context,
        ),
        patch(
            "events_aggregator.services.outbox_worker.SqlAlchemyOutboxRepository",
            return_value=repository,
        ),
        patch(
            "events_aggregator.services.outbox_worker.asyncio.sleep",
            side_effect=StopWorker,
        ),
        pytest.raises(StopWorker),
    ):
        await outbox_worker(client)

    client.send_notification.assert_awaited_once_with(
        message="Вы успешно зарегистрированы на мероприятие - Python Meetup",
        reference_id=str(ticket_id),
        idempotency_key=str(outbox.id),
    )


@pytest.mark.asyncio
async def test_mark_as_sent() -> None:
    """Проверяет перевод outbox-события в статус SENT после отправки"""

    ticket_id = uuid.uuid4()

    outbox = Outbox(
        event_type="ticket_purchased",
        payload={
            "ticket_id": str(ticket_id),
            "event_name": "Python Meetup",
        },
        status=OutboxStatus.PENDING,
    )

    client = AsyncMock()

    session = AsyncMock()
    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=session)

    repository = MagicMock()
    repository.get_pending = AsyncMock(return_value=[outbox])

    with (
        patch(
            "events_aggregator.services.outbox_worker.async_session_maker",
            return_value=session_context,
        ),
        patch(
            "events_aggregator.services.outbox_worker.SqlAlchemyOutboxRepository",
            return_value=repository,
        ),
        patch(
            "events_aggregator.services.outbox_worker.asyncio.sleep",
            side_effect=StopWorker,
        ),
        pytest.raises(StopWorker),
    ):
        await outbox_worker(client)

    assert outbox.status == OutboxStatus.SENT
    session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_send_failure() -> None:
    """Проверяет обработку ошибки отправки уведомления"""

    ticket_id = uuid.uuid4()

    outbox = Outbox(
        event_type="ticket_purchased",
        payload={
            "ticket_id": str(ticket_id),
            "event_name": "Python Meetup",
        },
        status=OutboxStatus.PENDING,
    )

    client = AsyncMock()
    client.send_notification.side_effect = RuntimeError("Capashino error")

    session = AsyncMock()
    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=session)

    repository = MagicMock()
    repository.get_pending = AsyncMock(return_value=[outbox])

    with (
        patch(
            "events_aggregator.services.outbox_worker.async_session_maker",
            return_value=session_context,
        ),
        patch(
            "events_aggregator.services.outbox_worker.SqlAlchemyOutboxRepository",
            return_value=repository,
        ),
        patch(
            "events_aggregator.services.outbox_worker.asyncio.sleep",
            side_effect=StopWorker,
        ),
        pytest.raises(StopWorker),
    ):
        await outbox_worker(client)

    assert outbox.status == OutboxStatus.PENDING
