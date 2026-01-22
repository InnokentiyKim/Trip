from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.infrastructure.database.postgres.config import DatabaseSettings


def create_database_adapter(config: DatabaseSettings) -> AsyncEngine:
    """Creates and returns an asynchronous SQLAlchemy engine for database interaction.

    Args:
        config (DatabaseSettings): The database configuration settings.
    """
    return create_async_engine(config.db_url, **config.engine.model_dump())
