from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.config import settings


class DatabaseHelper:
    def __init__(self, *, url: str, echo: bool = False):

        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()


db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
)
