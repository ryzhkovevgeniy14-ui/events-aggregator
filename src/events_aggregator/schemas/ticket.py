from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """
    Модель запроса на регистрацию участника.

    Используется для регистрации на мероприятие.
    Содержит данные участника, идентификатор события и выбранное место.
    """
    event_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    seat: str
    idempotency_key: str | None = None


class RegisterResponse(BaseModel):
    """
    Модель ответа после регистрации участника.

    Используется для возврата идентификатора созданного билета.
    """
    ticket_id: UUID


class UnregisterResponse(BaseModel):
    """
    Модель ответа после отмены регистрации.

    Содержит признак успешного выполнения операции.
    """
    success: bool