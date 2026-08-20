from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from events_aggregator.schemas.place import PlaceResponse


class EventResponse(BaseModel):
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


class EventsResponse(BaseModel):
    next: str | None
    previous: str | None
    results: list[EventResponse]