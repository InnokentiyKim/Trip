from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncSessionTransaction, create_async_engine

from src.common.interfaces import UowProto
from src.infrastructure.context import RequestContext
from src.infrastructure.database.postgres.config import DatabaseSettings


def create_database_adapter(config: DatabaseSettings) -> AsyncEngine:
    """Creates and returns an asynchronous SQLAlchemy engine for database interaction.

    Args:
        config (DatabaseSettings): The database configuration settings.
    """
    return create_async_engine(config.db_url, **config.engine.model_dump())


class SqlAlchemyUnitOfWork(UowProto):
    """SQLAlchemy unit of work implementation.

    The class wraps the already existing SQLAlchemy unit of work implementations for easier usage.
    """

    def __init__(
        self,
        session: AsyncSession,
        request_context: RequestContext,
        transaction: AsyncSessionTransaction | None = None,
    ) -> None:
        self.session: AsyncSession = session
        self.request_context = request_context
        self.transaction: AsyncSessionTransaction | None = transaction

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self.transaction is not None:
            await self.transaction.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        if self.transaction is not None:
            await self.transaction.rollback()

    async def __aenter__(self) -> Self:
        """Start a transaction on the current session and return the UoW instance."""
        self.transaction = self.transaction or self.session.begin()
        await self.transaction.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the current transaction and commit or rollback based on the result."""
        if self.transaction is not None:
            await self.transaction.__aexit__(exc_type, exc_value, traceback)
        self.transaction = None

        return
