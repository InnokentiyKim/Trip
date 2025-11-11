from uuid import UUID

from sqlalchemy.exc import IntegrityError
from typing import Any
from sqlalchemy import select

from src.common.exceptions.common import BaseError
from src.common.interfaces import SQLAlchemyGatewayProto
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.domain.models import ORM_OBJ, ORM_CLS


class SQLAlchemyGateway(SQLAlchemyGatewayProto):
    """SQLAlchemy adapters implementing the gateway protocol."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_item(self, session: AsyncSession, item: ORM_OBJ) -> None:
        session.add(item)
        try:
            await session.commit()
        except IntegrityError:
            raise BaseError(status_code=409, message="Item already exists") from None

    async def get_item_by_id(self, session: AsyncSession, orm_cls: ORM_CLS, item_id: int | UUID) -> ORM_OBJ | None:
        item = await session.get(orm_cls, item_id)
        return item

    async def get_one_item(self, session: AsyncSession, orm_cls: ORM_CLS, **filters: Any) -> ORM_OBJ | None:
        query = select(orm_cls).filter_by(**filters)
        row = await session.execute(query)
        return row.scalar_one_or_none()

    async def get_items_list(self, session: AsyncSession, orm_cls: ORM_CLS, **filters: Any) -> list[ORM_OBJ]:
        query = select(orm_cls).filter_by(**filters)
        rows = await session.execute(query)
        return list(rows)

    async def delete_item(self, session: AsyncSession, orm_obj: ORM_OBJ) -> None:
        await session.delete(orm_obj)
        await session.commit()
