from __future__ import annotations

from datetime import date
from uuid import UUID

import httpx

from events_aggregator.schemas.event import EventsResponse
from events_aggregator.schemas.seats import SeatsResponse
from events_aggregator.schemas.ticket import RegisterResponse, UnregisterResponse


class EventsProviderClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = client

    async def events(
        self,
        changed_at: date,
        url: str | None = None,
    ) -> EventsResponse:
        if url is None:
            url = f"{self.base_url}/api/events/"

            response = await self.client.get(
                url,
                params={"changed_at": changed_at.isoformat()},
                headers={"x-api-key": self.api_key},
            )
        else:
            response = await self.client.get(
                url,
                headers={"x-api-key": self.api_key},
            )

        response.raise_for_status()

        return EventsResponse.model_validate(response.json())

    async def seats(self, event_id: UUID) -> SeatsResponse:
        response = await self.client.get(
            f"{self.base_url}/api/events/{event_id}/seats/",
            headers={"x-api-key": self.api_key},
        )

        response.raise_for_status()

        return SeatsResponse.model_validate(response.json())

    async def register(
        self,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> RegisterResponse:
        response = await self.client.post(
            f"{self.base_url}/api/events/{event_id}/register/",
            headers={"x-api-key": self.api_key},
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "seat": seat,
            },
        )

        response.raise_for_status()

        return RegisterResponse.model_validate(response.json())

    async def unregister(
        self,
        event_id: UUID,
        ticket_id: UUID,
    ) -> UnregisterResponse:
        response = await self.client.request(
            "DELETE",
            f"{self.base_url}/api/events/{event_id}/unregister/",
            headers={"x-api-key": self.api_key},
            json={"ticket_id": str(ticket_id)},
        )

        response.raise_for_status()

        return UnregisterResponse.model_validate(response.json())