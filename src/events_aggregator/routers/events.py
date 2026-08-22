from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from events_aggregator.dependencies import (
    get_event_repository,
    get_seats_service,
)
from events_aggregator.repositories.event import EventRepository
from events_aggregator.schemas.event import (
    EventListItem,
    EventResponse,
    EventsListResponse,
)
from events_aggregator.schemas.seats import SeatsResponse
from events_aggregator.services.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
)
from events_aggregator.services.seats import SeatsService

router = APIRouter()


@router.get("/api/events", response_model=EventsListResponse)
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


@router.get("/api/events/{event_id}", response_model=EventResponse)
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


@router.get("/api/events/{event_id}/seats", response_model=SeatsResponse)
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