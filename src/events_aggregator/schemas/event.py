from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from events_aggregator.schemas.place import PlaceListItem, PlaceResponse


class EventResponse(BaseModel):
    """
    Модель события.

    Используется для представления данных события
    при получении его деталей и синхронизации с Events Provider API.
    Содержит полную информацию о событии и площадке.
    """
    id: UUID
    name: str
    place: PlaceResponse
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventsResponse(BaseModel):
    """
    Модель ответа Events Provider API со списком событий.

    Используется при получении и постраничном обходе событий
    во время синхронизации.
    Содержит ссылки на следующие страницы и список событий.
    """
    next: str | None
    previous: str | None
    results: list[EventResponse]


class EventListItem(BaseModel):
    """
    Модель события для списка.

    Используется в ответе API при получении списка событий.
    Содержит основные данные события и сокращённую информацию о площадке.
    """
    id: UUID
    name: str
    place: PlaceListItem
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int

    model_config = ConfigDict(from_attributes=True)


class EventsListResponse(BaseModel):
    """
    Модель ответа API со списком событий.

    Используется для возврата списка синхронизированных событий клиенту.
    Содержит количество событий, ссылки пагинации и список результатов.
    """
    count: int
    next: str | None
    previous: str | None
    results: list[EventListItem]