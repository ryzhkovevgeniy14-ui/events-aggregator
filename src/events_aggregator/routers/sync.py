from fastapi import APIRouter, Depends

from events_aggregator.dependencies import get_sync_service
from events_aggregator.services.sync import SyncService

router = APIRouter()


@router.post("/api/sync/trigger")
async def trigger_sync(
    sync_service: SyncService = Depends(get_sync_service),  # noqa: B008
) -> dict[str, str]:
    await sync_service.sync()

    return {"status": "ok"}