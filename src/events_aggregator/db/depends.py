from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.db.session import async_session_maker


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет асинхронную сессию БД в рамках транзакции."""
    async with async_session_maker() as session, session.begin():
        yield session