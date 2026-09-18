import time

from starlette.middleware.base import BaseHTTPMiddleware

from events_aggregator.core.metrics import (
    http_request_duration_seconds,
    http_requests_total,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.monotonic()

        response = await call_next(request)

        duration = time.monotonic() - start_time

        route = request.scope.get("route")
        endpoint = route.path if route else request.url.path

        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code,
        ).inc()

        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(duration)

        return response
