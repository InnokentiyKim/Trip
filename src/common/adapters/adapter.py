from typing import Any
from sqlalchemy import select
from src.common.interfaces import SQLAlchemyGatewayProto
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyGateway(SQLAlchemyGatewayProto):
    """SQLAlchemy adapter implementing the gateway protocol."""
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._model = None

    async def find_all(self, **filters: Any) -> list[Any]:
        """Find all model instances matching the given filters."""
        query = select(self._model).filter_by(**filters)
        result = await self._session.scalars(query)
        return list(result)

    async def find_one(self, **filters: Any) -> Any | None:
        """Find a single model instance matching the given filters."""
        query = select(self._model).filter_by(**filters)
        return await self._session.scalar(query)

    async def find_by_id(self, instance_id: int) -> Any | None:
        """Find a single model instance by its unique identifier."""
        query = select(self._model).filter_by(id=instance_id)
        return await self._session.scalar(query)
