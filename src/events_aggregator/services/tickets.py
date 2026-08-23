from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import httpx

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.enums import EventStatus, TicketStatus
from events_aggregator.models.ticket import Ticket
from events_aggregator.repositories.event import EventRepository
from events_aggregator.repositories.ticket import TicketRepository
from events_aggregator.schemas.ticket import RegisterResponse, UnregisterResponse
from events_aggregator.services.exceptions import (
    EventAlreadyPassedError,
    EventNotFoundError,
    EventNotPublishedError,
    RegistrationDeadlinePassedError,
    SeatNotAvailableError,
    TicketNotFoundError,
)


class TicketService:
    """
    Сервис регистрации и отмены регистрации на мероприятия.
    """
    def __init__(
        self,
        events: EventRepository,
        tickets: TicketRepository,
        client: EventsProviderClient,
    ) -> None:
        self.events = events
        self.tickets = tickets
        self.client = client

    async def register(
        self,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> RegisterResponse:
        """
        Регистрирует пользователя на мероприятие.

        Проверяет доступность мероприятия и места, выполняет
        регистрацию через Events Provider и сохраняет билет в базе данных.
        """
        event = await self.events.get(event_id)

        if event is None:
            raise EventNotFoundError("Event not found")

        if event.status != EventStatus.PUBLISHED:
            raise EventNotPublishedError("Event is not published")

        if datetime.now(timezone.utc) >= event.registration_deadline:
            raise RegistrationDeadlinePassedError(
                "Registration deadline has passed",
            )

        seats = await self.client.seats(event_id)

        if seat not in seats.seats:
            raise SeatNotAvailableError("Seat is not available")

        try:
            provider_response = await self.client.register(
                event_id=event_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                seat=seat,
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 400:
                raise SeatNotAvailableError(
                    "Seat is not available",
                ) from exc
            raise

        ticket = Ticket(
            ticket_id=provider_response.ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            status=TicketStatus.ACTIVE,
        )

        await self.tickets.create(ticket)

        return provider_response

    async def unregister(
        self,
        ticket_id: UUID,
    ) -> UnregisterResponse:
        """
        Отменяет регистрацию пользователя на мероприятие.

        Проверяет существование билета и то, что мероприятие ещё не началось,
        затем отменяет регистрацию через Events Provider.
        """
        ticket = await self.tickets.get(ticket_id)

        if ticket is None:
            raise TicketNotFoundError("Ticket not found")

        event = await self.events.get(ticket.event_id)

        if event is None:
            raise EventNotFoundError("Event not found")

        if datetime.now(timezone.utc) >= event.event_time:
            raise EventAlreadyPassedError(
                "Event has already passed",
            )

        response = await self.client.unregister(
            event_id=ticket.event_id,
            ticket_id=ticket_id,
        )

        ticket.status = TicketStatus.CANCELLED

        return response