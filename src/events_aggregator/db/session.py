from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from events_aggregator.core.config import settings

database_url = settings.postgres_connection_string.replace(
    "postgres://",
    "postgresql+asyncpg://",
)

# Асинхронный движок SQLAlchemy для работы с PostgreSQL
async_engine = create_async_engine(
    database_url,
    echo=True,
)

# Фабрика асинхронных сессий, используемая dependency-функциями
async_session_maker = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)