from __future__ import annotations

import asyncio
from urllib.parse import urljoin

import httpx


class CapashinoClient:
    """
    Клиент для взаимодействия с Capashino API.
    """

    MAX_ATTEMPTS = 3
    RETRY_DELAYS = (1, 2)

    def __init__(
        self,
        base_url: str,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = client

    async def send_notification(
        self,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ) -> None:
        """
        Отправляет уведомление в Capashino.

        Повторяет запрос при ответе с ошибкой 5xx.
        При остальных HTTP-ошибках сразу вызывает исключение.
        """
        url = urljoin(
            self.base_url,
            "api/notifications",
        )

        headers = {
            "X-API-Key": self.api_key,
        }

        payload = {
            "message": message,
            "reference_id": reference_id,
            "idempotency_key": idempotency_key,
        }

        for attempt in range(self.MAX_ATTEMPTS):
            response = await self.client.post(
                url,
                headers=headers,
                json=payload,
            )

            if response.status_code < 500:
                response.raise_for_status()
                return

            if attempt < self.MAX_ATTEMPTS - 1:
                await asyncio.sleep(self.RETRY_DELAYS[attempt])
                continue

            response.raise_for_status()