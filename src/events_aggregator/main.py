from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.db.depends import get_async_db

app = FastAPI(title="Events Aggregator")


@app.get("/api/health")
async def health_check(
    db: AsyncSession = Depends(get_async_db),  # noqa: B008
) -> dict[str, str]:
    await db.execute(text("SELECT 1"))

    return {"status": "ok"}