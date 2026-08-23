from __future__ import annotations

import asyncio
from datetime import date
from urllib.parse import urljoin
from uuid import UUID

import httpx

from events_aggregator.schemas.event import EventsResponse
from events_aggregator.schemas.seats import ProviderSeatsResponse
from events_aggregator.schemas.ticket import RegisterResponse, UnregisterResponse


class EventsProviderClient:
    """
    Клиент для взаимодействия с Events Provider API.

    Отвечает за выполнение HTTP-запросов к внешнему сервису,
    передачу API-ключа, обработку временных ошибок и преобразование
    ответов в Pydantic-модели.
    """
    MAX_ATTEMPTS = 3  # Максимальное количество попыток одного HTTP-запроса
    RETRY_DELAYS = (1, 2)  # Задержки между повторными попытками в секундах

    def __init__(
        self,
        base_url: str,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = client

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        """
        Выполняет HTTP-запрос с повторными попытками.

        Повторяет запрос при временной ошибке соединения
        с задержками, заданными в RETRY_DELAYS.
        """
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                response = await self.client.request(
                    method,
                    url,
                    **kwargs,
                )
                response.raise_for_status()
                return response

            except httpx.RequestError:
                if attempt == self.MAX_ATTEMPTS - 1:
                    raise

                await asyncio.sleep(self.RETRY_DELAYS[attempt])

        raise RuntimeError("Request failed")

    async def events(
        self,
        changed_at: date,
        url: str | None = None,
    ) -> EventsResponse:
        """
        Получает страницу событий из Events Provider API.

        Для первого запроса использует параметр changed_at.
        Для последующих страниц использует URL из поля next,
        полученного от API.
        """
        if url is None:
            url = urljoin(self.base_url, "api/events/")

            response = await self._request(
                "GET",
                url,
                params={"changed_at": changed_at.isoformat()},
                headers={"x-api-key": self.api_key},
            )
        else:
            response = await self._request(
                "GET",
                url,
                headers={"x-api-key": self.api_key},
            )

        return EventsResponse.model_validate(response.json())

    async def seats(self, event_id: UUID) -> ProviderSeatsResponse:
        """
        Получает актуальный список свободных мест мероприятия.
        Выполняет запрос непосредственно к Events Provider API.
        """
        response = await self._request(
            "GET",
            urljoin(self.base_url, f"api/events/{event_id}/seats/"),
            headers={"x-api-key": self.api_key},
        )

        return ProviderSeatsResponse.model_validate(response.json())

    async def register(
        self,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> RegisterResponse:
        """
        Регистрирует участника на мероприятие через Events Provider API.
        Передаёт данные участника и выбранное место.
        """
        response = await self._request(
            "POST",
            urljoin(self.base_url, f"api/events/{event_id}/register/"),
            headers={"x-api-key": self.api_key},
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "seat": seat,
            },
        )

        return RegisterResponse.model_validate(response.json())

    async def unregister(
        self,
        event_id: UUID,
        ticket_id: UUID,
    ) -> UnregisterResponse:
        """
        Отменяет регистрацию участника через Events Provider API.
        Для отмены передаёт идентификатор билета.
        """
        response = await self._request(
            "DELETE",
            urljoin(self.base_url, f"api/events/{event_id}/unregister/"),
            headers={"x-api-key": self.api_key},
            json={"ticket_id": str(ticket_id)},
        )

        return UnregisterResponse.model_validate(response.json())