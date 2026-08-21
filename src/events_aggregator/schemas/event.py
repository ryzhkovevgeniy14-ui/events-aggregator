from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from events_aggregator.schemas.place import PlaceListItem, PlaceResponse


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

    model_config = ConfigDict(from_attributes=True)


class EventsResponse(BaseModel):
    next: str | None
    previous: str | None
    results: list[EventResponse]


class EventListItem(BaseModel):
    id: UUID
    name: str
    place: PlaceListItem
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int

    model_config = ConfigDict(from_attributes=True)


class EventsListResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventListItem]