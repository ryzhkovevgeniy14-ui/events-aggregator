from uuid import UUID

from pydantic import BaseModel


class ProviderSeatsResponse(BaseModel):
    """
    Модель ответа Events Provider API со свободными местами.

    Используется при получении актуального списка свободных мест.
    Содержит список доступных мест.
    """
    seats: list[str]


class SeatsResponse(BaseModel):
    """
    Модель ответа API со свободными местами мероприятия.

    Используется для возврата актуального списка доступных мест клиенту.
    Содержит идентификатор события и список свободных мест.
    """
    event_id: UUID
    available_seats: list[str]