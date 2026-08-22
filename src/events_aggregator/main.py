from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from events_aggregator.routers import events, health, sync, tickets
from events_aggregator.services.sync_worker import sync_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        app.state.seats_cache = {}

        worker = asyncio.create_task(sync_worker(client))

        try:
            yield
        finally:
            worker.cancel()
            await worker


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


app.include_router(health.router)
app.include_router(sync.router)
app.include_router(events.router)
app.include_router(tickets.router)