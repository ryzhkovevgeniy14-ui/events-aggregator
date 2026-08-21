from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime, time

import httpx
from fastapi import Depends, FastAPI, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.db.depends import get_async_db
from events_aggregator.dependencies import (
    get_event_repository,
    get_sync_service,
)
from events_aggregator.repositories.event import EventRepository
from events_aggregator.schemas.event import EventListItem, EventsListResponse
from events_aggregator.services.sync import SyncService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield


app = FastAPI(
    title="Events Aggregator",
    lifespan=lifespan,
)


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