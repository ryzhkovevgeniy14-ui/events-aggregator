from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.db.depends import get_async_db

router = APIRouter()


@router.get("/api/health")
async def health_check(
    db: AsyncSession = Depends(get_async_db),  # noqa: B008
) -> dict[str, str]:
    """
    Проверяет доступность приложения и подключения к базе данных.
    """
    await db.execute(text("SELECT 1"))

    return {"status": "ok"}