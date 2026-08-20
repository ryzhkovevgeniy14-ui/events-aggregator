from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.db.depends import get_async_db
from events_aggregator.dependencies import get_sync_service
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