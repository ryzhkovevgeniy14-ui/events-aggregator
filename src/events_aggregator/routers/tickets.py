from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from events_aggregator.dependencies import get_ticket_service
from events_aggregator.schemas.ticket import (
    RegisterRequest,
    RegisterResponse,
    UnregisterResponse,
)
from events_aggregator.services.exceptions import (
    EventAlreadyPassedError,
    EventNotFoundError,
    RegistrationDeadlinePassedError,
    SeatNotAvailableError,
    TicketNotFoundError,
)
from events_aggregator.services.tickets import TicketService

router = APIRouter()


@router.post(
    "/api/tickets",
    response_model=RegisterResponse,
    status_code=201,
)
async def register_ticket(
    data: RegisterRequest,
    ticket_service: TicketService = Depends(get_ticket_service),  # noqa: B008
) -> RegisterResponse:
    try:
        return await ticket_service.register(
            event_id=data.event_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            seat=data.seat,
        )
    except RegistrationDeadlinePassedError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except SeatNotAvailableError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.delete(
    "/api/tickets/{ticket_id}",
    response_model=UnregisterResponse,
)
async def unregister_ticket(
    ticket_id: UUID,
    ticket_service: TicketService = Depends(get_ticket_service),  # noqa: B008
) -> UnregisterResponse:
    try:
        return await ticket_service.unregister(ticket_id)
    except TicketNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
    except EventNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
    except EventAlreadyPassedError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )