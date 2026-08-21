from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: str
    changed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PlaceListItem(BaseModel):
    id: UUID
    name: str
    city: str
    address: str

    model_config = ConfigDict(from_attributes=True)