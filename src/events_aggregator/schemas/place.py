from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceResponse(BaseModel):
    """
    Модель полной информации о площадке.

    Используется при получении деталей события.
    Содержит данные площадки, включая схему рассадки.
    """
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: str
    changed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaceListItem(BaseModel):
    """
    Модель площадки для списка событий.

    Используется при получении списка событий.
    Содержит основные данные площадки без схемы рассадки.
    """
    id: UUID
    name: str
    city: str
    address: str

    model_config = ConfigDict(from_attributes=True)