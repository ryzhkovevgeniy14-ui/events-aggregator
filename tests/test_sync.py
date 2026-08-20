from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from events_aggregator.models.sync_state import SyncState
from events_aggregator.schemas.event import EventResponse
from events_aggregator.schemas.place import PlaceResponse
from events_aggregator.services.sync import SyncService


class EmptyPaginator:
    """
    Имитирует EventsPaginator, который не возвращает событий.
    """

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


class FailingPaginator:
    """
    Имитирует EventsPaginator, который выбрасывает ошибку
    при попытке получить первое событие.
    """

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise RuntimeError("Provider unavailable")


def create_event() -> EventResponse:
    """
    Создаёт тестовое событие вместе с площадкой.

    Используется как данные, которые условно пришли
    из Events Provider во время синхронизации.
    """
    place = PlaceResponse(
        id="650e8400-e29b-41d4-a716-446655440001",
        name="Конференц-зал",
        city="Москва",
        address="ул. Ленина, д. 1",
        seats_pattern="A1-1000",
        changed_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    return EventResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Python Conference",
        place=place,
        event_time=datetime(
            2026,
            1,
            11,
            tzinfo=timezone.utc,
        ),
        registration_deadline=datetime(
            2026,
            1,
            10,
            tzinfo=timezone.utc,
        ),
        status="published",
        number_of_visitors=5,
        changed_at=datetime(
            2026,
            1,
            4,
            tzinfo=timezone.utc,
        ),
        created_at=datetime(
            2026,
            1,
            4,
            tzinfo=timezone.utc,
        ),
        status_changed_at=datetime(
            2026,
            1,
            4,
            tzinfo=timezone.utc,
        ),
    )


@pytest.mark.asyncio
async def test_first_sync(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Проверяет первую синхронизацию.

    Если SyncState отсутствует, сервис считает синхронизацию
    первой и использует дату 2000-01-01 для получения всех
    событий из Events Provider.

    После получения события сервис должен сохранить площадку,
    событие и завершить синхронизацию со статусом success.
    """
    client = Mock()

    events = AsyncMock()
    places = AsyncMock()
    sync_state = AsyncMock()

    events.get.return_value = None
    places.get.return_value = None
    sync_state.get.return_value = None

    event = create_event()

    paginator = Mock()

    async def iterate():
        yield event

    paginator.__aiter__ = lambda self: iterate()

    paginator_class = Mock(return_value=paginator)

    monkeypatch.setattr(
        "events_aggregator.services.sync.EventsPaginator",
        paginator_class,
    )

    service = SyncService(
        client=client,
        events=events,
        places=places,
        sync_state=sync_state,
    )

    await service.sync()

    paginator_class.assert_called_once_with(
        client=client,
        changed_at=date(2000, 1, 1),
    )

    places.get.assert_awaited_once_with(event.place.id)
    events.get.assert_awaited_once_with(event.id)

    places.save.assert_awaited_once()
    events.save.assert_awaited_once()

    state = sync_state.save.call_args_list[-1].args[0]

    assert state.last_changed_at == event.changed_at
    assert state.sync_status == "success"
    assert state.last_sync_time is not None


@pytest.mark.asyncio
async def test_incremental_sync(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Проверяет инкрементальную синхронизацию.

    Если SyncState уже существует и содержит last_changed_at,
    сервис должен использовать дату предыдущей синхронизации
    вместо начальной даты 2000-01-01.

    При отсутствии новых событий синхронизация должна
    завершиться со статусом success.
    """
    client = Mock()

    events = AsyncMock()
    places = AsyncMock()
    sync_state = AsyncMock()

    last_changed_at = datetime(
        2026,
        1,
        3,
        15,
        30,
        tzinfo=timezone.utc,
    )

    sync_state.get.return_value = SyncState(
        last_sync_time=datetime(
            2026,
            1,
            3,
            tzinfo=timezone.utc,
        ),
        last_changed_at=last_changed_at,
        sync_status="success",
    )

    paginator_class = Mock(
        return_value=EmptyPaginator(),
    )

    monkeypatch.setattr(
        "events_aggregator.services.sync.EventsPaginator",
        paginator_class,
    )

    service = SyncService(
        client=client,
        events=events,
        places=places,
        sync_state=sync_state,
    )

    await service.sync()

    paginator_class.assert_called_once_with(
        client=client,
        changed_at=last_changed_at.date(),
    )

    state = sync_state.save.call_args_list[-1].args[0]

    assert state.last_changed_at == last_changed_at
    assert state.sync_status == "success"


@pytest.mark.asyncio
async def test_sync_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Проверяет обработку ошибки во время синхронизации.

    Если EventsPaginator выбрасывает исключение, SyncService
    должен изменить статус синхронизации на failed, сохранить
    это состояние и повторно выбросить исходную ошибку.
    """
    client = Mock()

    events = AsyncMock()
    places = AsyncMock()
    sync_state = AsyncMock()

    sync_state.get.return_value = None

    paginator_class = Mock(
        return_value=FailingPaginator(),
    )

    monkeypatch.setattr(
        "events_aggregator.services.sync.EventsPaginator",
        paginator_class,
    )

    service = SyncService(
        client=client,
        events=events,
        places=places,
        sync_state=sync_state,
    )

    with pytest.raises(
        RuntimeError,
        match="Provider unavailable",
    ):
        await service.sync()

    state = sync_state.save.call_args_list[-1].args[0]

    assert state.sync_status == "failed"