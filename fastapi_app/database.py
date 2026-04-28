import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

database_url = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres"
)

engine = create_async_engine(database_url, pool_pre_ping=True, future=True)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
