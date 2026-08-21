from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.models.ticket import Ticket
from events_aggregator.repositories.event import EventRepository
from events_aggregator.repositories.ticket import TicketRepository
from events_aggregator.schemas.ticket import RegisterResponse, UnregisterResponse


class EventNotFoundError(ValueError):
    pass


class EventNotPublishedError(ValueError):
    pass


class RegistrationDeadlinePassedError(ValueError):
    pass


class SeatNotAvailableError(ValueError):
    pass


class TicketNotFoundError(ValueError):
    pass


class EventAlreadyPassedError(ValueError):
    pass


class TicketService:
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
        event = await self.events.get(event_id)

        if event is None:
            raise EventNotFoundError("Event not found")

        if event.status != "published":
            raise EventNotPublishedError("Event is not published")

        if datetime.now(timezone.utc) >= event.registration_deadline:
            raise RegistrationDeadlinePassedError(
                "Registration deadline has passed",
            )

        seats = await self.client.seats(event_id)

        if seat not in seats.seats:
            raise SeatNotAvailableError("Seat is not available")

        provider_response = await self.client.register(
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )

        ticket = Ticket(
            ticket_id=provider_response.ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            status="active",
        )

        await self.tickets.create(ticket)

        return provider_response

    async def unregister(
        self,
        ticket_id: UUID,
    ) -> UnregisterResponse:
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

        ticket.status = "cancelled"

        return response