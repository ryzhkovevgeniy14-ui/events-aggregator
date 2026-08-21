from uuid import UUID

from pydantic import BaseModel


class ProviderSeatsResponse(BaseModel):
    seats: list[str]


class SeatsResponse(BaseModel):
    event_id: UUID
    available_seats: list[str]