from __future__ import annotations

import asyncio

from events_aggregator.clients.capashino import CapashinoClient
from events_aggregator.core.config import settings
from events_aggregator.core.enums import OutboxStatus
from events_aggregator.core.logging import logger
from events_aggregator.db.session import async_session_maker
from events_aggregator.repositories.outbox_sqlalchemy import (
    SqlAlchemyOutboxRepository,
)


async def outbox_worker(
    client: CapashinoClient,
) -> None:
    """Периодически отправляет ожидающие события в Capashino."""
    while True:
        async with async_session_maker() as session:
            repository = SqlAlchemyOutboxRepository(session)

            outbox_events = await repository.get_pending(
                limit=settings.outbox_batch_size,
            )

            await session.commit()

            for outbox in outbox_events:
                try:
                    await client.send_notification(
                        message=(
                            "Вы успешно зарегистрированы "
                            f"на мероприятие - {outbox.payload['event_name']}"
                        ),
                        reference_id=outbox.payload["ticket_id"],
                        idempotency_key=str(outbox.id),
                    )

                except Exception:  # noqa: BLE001
                    logger.exception(
                        "Failed to send outbox event %s",
                        outbox.id,
                    )
                    continue

                outbox.status = OutboxStatus.SENT
                await session.commit()

        await asyncio.sleep(settings.outbox_interval)