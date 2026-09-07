from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import httpx
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration

from events_aggregator.clients.capashino import CapashinoClient
from events_aggregator.core.config import settings
from events_aggregator.routers import events, health, sync, tickets
from events_aggregator.services.outbox_worker import outbox_worker
from events_aggregator.services.sync_worker import sync_worker

sentry_sdk.init(
    dsn=settings.glitchtip_dsn,
    integrations=[FastApiIntegration()],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет ресурсами приложения в течение его жизненного цикла."""
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        app.state.seats_cache = {}

        capashino_client = CapashinoClient(
            base_url=settings.capashino_base_url,
            api_key=settings.capashino_api_key,
            client=client,
        )

        sync_task = asyncio.create_task(sync_worker(client))
        outbox_task = asyncio.create_task(
            outbox_worker(capashino_client),
        )

        try:
            yield
        finally:
            # Останавливаем фоновые задачи перед завершением приложения
            sync_task.cancel()
            outbox_task.cancel()

            await sync_task
            await outbox_task


app = FastAPI(
    title="Events Aggregator",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Возвращает ошибки валидации в формате, ожидаемом API."""
    if request.url.path == "/api/tickets":
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors()},
        )

    return await request_validation_exception_handler(request, exc)


@app.get("/api/test-error")
async def test_error():
    """Тестовый эндпоинт для проверки отправки исключений в GlitchTip."""
    raise RuntimeError("GlitchTip integration test")


app.include_router(health.router)
app.include_router(sync.router)
app.include_router(events.router)
app.include_router(tickets.router)