from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError
from typing import Any
from sqlalchemy import select
from src.common.interfaces import SQLAlchemyGatewayProto
from src.common.domain.models import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.domain.models import ORM_OBJ, ORM_CLS


class SQLAlchemyGateway(SQLAlchemyGatewayProto):
    """SQLAlchemy adapters implementing the gateway protocol."""
    async def add_item(self, session: AsyncSession, item: ORM_OBJ) -> None:
        session.add(item)
        try:
            await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Item already exists")

    async def get_item_by_id(self, session: AsyncSession, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJ:
        item = await session.get(orm_cls, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    async def get_all_items(self, session: AsyncSession, orm_cls: ORM_CLS, **filters: Any) -> list[ORM_OBJ]:
        query = select(orm_cls).filter_by(**filters)
        rows = await session.execute(query)
        return list(rows)

    async def delete_item(self, session: AsyncSession, orm_obj: ORM_OBJ) -> None:
        await session.delete(orm_obj)
        await session.commit()
