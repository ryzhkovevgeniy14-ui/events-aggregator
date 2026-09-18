from fastapi import APIRouter, Depends
from fastapi.responses import Response
from prometheus_client import REGISTRY, generate_latest

from events_aggregator.core.metrics import (
    events_total,
    tickets_cancelled_total,
    tickets_created_total,
)
from events_aggregator.dependencies import (
    get_event_repository,
    get_ticket_repository,
)
from events_aggregator.repositories.event import EventRepository
from events_aggregator.repositories.ticket import TicketRepository

router = APIRouter()


@router.get("/metrics")
async def metrics(
    events_repo: EventRepository = Depends(get_event_repository),  # noqa: B008
    tickets_repo: TicketRepository = Depends(get_ticket_repository),  # noqa: B008
):
    events_total.set(await events_repo.count())
    tickets_created_total.set(await tickets_repo.count())
    tickets_cancelled_total.set(await tickets_repo.count_cancelled())

    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain",
    )
