from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    seat: str


class RegisterResponse(BaseModel):
    ticket_id: UUID


class UnregisterResponse(BaseModel):
    success: bool