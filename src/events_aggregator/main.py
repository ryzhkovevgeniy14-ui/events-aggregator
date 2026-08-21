from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime, time
from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.db.depends import get_async_db
from events_aggregator.dependencies import (
    get_event_repository,
    get_seats_service,
    get_sync_service,
    get_ticket_service,
)
from events_aggregator.repositories.event import EventRepository
from events_aggregator.schemas.event import (
    EventListItem,
    EventResponse,
    EventsListResponse,
)
from events_aggregator.schemas.seats import SeatsResponse
from events_aggregator.schemas.ticket import RegisterRequest, RegisterResponse
from events_aggregator.services.seats import (
    EventNotFoundError,
    EventNotPublishedError,
    SeatsService,
)
from events_aggregator.services.sync import SyncService
from events_aggregator.services.tickets import (
    RegistrationDeadlinePassedError,
    SeatNotAvailableError,
    TicketService,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        app.state.seats_cache = {}
        yield


app = FastAPI(
    title="Events Aggregator",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    if request.url.path == "/api/tickets":
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors()},
        )

    return await request_validation_exception_handler(request, exc)


@app.get("/api/health")
async def health_check(
    db: AsyncSession = Depends(get_async_db),  # noqa: B008
) -> dict[str, str]:
    await db.execute(text("SELECT 1"))

    return {"status": "ok"}


@app.post("/api/sync/trigger")
async def trigger_sync(
    sync_service: SyncService = Depends(get_sync_service),  # noqa: B008
) -> dict[str, str]:
    await sync_service.sync()

    return {"status": "ok"}


@app.get("/api/events", response_model=EventsListResponse)
async def list_events(
    request: Request,
    date_from: date | None = None,
    page: int = 1,
    page_size: int = 20,
    events: EventRepository = Depends(get_event_repository),  # noqa: B008
) -> EventsListResponse:
    date_from_datetime = (
        datetime.combine(date_from, time.min)
        if date_from is not None
        else None
    )

    events_list, count = await events.list(
        date_from=date_from_datetime,
        page=page,
        page_size=page_size,
    )

    results = [
        EventListItem.model_validate(event)
        for event in events_list
    ]

    next_url = None
    if page * page_size < count:
        next_params: dict[str, int | str] = {
            "page": page + 1,
            "page_size": page_size,
        }

        if date_from is not None:
            next_params["date_from"] = date_from.isoformat()

        next_url = str(
            request.url.replace_query_params(**next_params)
        )

    previous_url = None
    if page > 1:
        previous_params: dict[str, int | str] = {
            "page": page - 1,
            "page_size": page_size,
        }

        if date_from is not None:
            previous_params["date_from"] = date_from.isoformat()

        previous_url = str(
            request.url.replace_query_params(**previous_params)
        )

    return EventsListResponse(
        count=count,
        next=next_url,
        previous=previous_url,
        results=results,
    )


@app.get(
    "/api/events/{event_id}",
    response_model=EventResponse,
)
async def get_event(
    event_id: UUID,
    events: EventRepository = Depends(get_event_repository),  # noqa: B008
) -> EventResponse:
    event = await events.get(event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return EventResponse.model_validate(event)


@app.get(
    "/api/events/{event_id}/seats",
    response_model=SeatsResponse,
)
async def get_event_seats(
    event_id: UUID,
    seats_service: SeatsService = Depends(get_seats_service),  # noqa: B008
) -> SeatsResponse:
    try:
        return await seats_service.get_seats(event_id)
    except EventNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )
    except EventNotPublishedError:
        raise HTTPException(
            status_code=400,
            detail="Event is not published",
        )


@app.post(
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