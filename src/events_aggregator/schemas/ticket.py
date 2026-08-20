from uuid import UUID

from pydantic import BaseModel


class RegisterResponse(BaseModel):
    ticket_id: UUID


class UnregisterResponse(BaseModel):
    success: bool