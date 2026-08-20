from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.db.session import async_session_maker


# Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session