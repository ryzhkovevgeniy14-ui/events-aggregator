from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import REGISTRY, generate_latest

router = APIRouter()


@router.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain",
    )
