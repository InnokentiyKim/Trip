import typing
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from typing import Any
from sqlalchemy import select
from fastapi import status
from src.common.exceptions.common import BaseError
from src.common.interfaces import SQLAlchemyGatewayProto
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.domain.models import ORM_OBJ, ORM_CLS
from src.infrastructure.database.memory.database import MemoryDatabase


class SQLAlchemyGateway(SQLAlchemyGatewayProto):
    """SQLAlchemy adapters implementing the gateway protocol."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, item: ORM_OBJ) -> None:
        self.session.add(item)
        try:
            await self.session.commit()
        except IntegrityError:
            raise BaseError(
                status_code=status.HTTP_409_CONFLICT, message="Item already exists"
            ) from None

    async def get_item_by_id(
        self, orm_cls: ORM_CLS, item_id: int | UUID
    ) -> ORM_OBJ | None:
        item = await self.session.get(orm_cls, item_id)
        return item

    async def get_one_item(self, orm_cls: ORM_CLS, **filters: Any) -> ORM_OBJ | None:
        query = select(orm_cls).filter_by(**filters)
        row = await self.session.execute(query)
        return row.scalar_one_or_none()

    async def get_items_list(self, orm_cls: ORM_CLS, **filters: Any) -> list[ORM_OBJ]:
        query = select(orm_cls).filter_by(**filters)
        rows = await self.session.execute(query)
        return list(rows)

    async def delete_item(self, orm_obj: ORM_OBJ) -> None:
        await self.session.delete(orm_obj)
        await self.session.commit()


class FakeGateway[Model]:
    def __init__(self, memory_db: MemoryDatabase) -> None:
        # Automatically discover the collection by iterating memory_db attributes
        self._collection = self._find_collection_by_type(memory_db)

    def _find_collection_by_type(self, memory_db: MemoryDatabase) -> set[Model]:
        """Find the collection in memory_db that contains instances of Model type.

        Uses Pydantic model fields to find collections with matching type annotations.

        Args:
            memory_db: The memory database instance containing collections.

        Returns:
            set[Model]: The collection containing Model instances.

        Raises:
            ValueError: If no matching collection is found.
        """
        model_type = self._get_model_type()

        # Use Pydantic model_fields from the class (not instance) to avoid deprecation warnings
        for field_name, field_info in memory_db.__class__.model_fields.items():
            # Check if field annotation is set[ModelType]
            annotation = field_info.annotation
            if annotation is None:
                continue

            # Handle set[SomeType] annotations
            if hasattr(annotation, "__origin__") and annotation.__origin__ is set:
                args = typing.get_args(annotation)
                if args and args[0] is model_type:
                    # Found matching field by type annotation
                    attr = getattr(memory_db, field_name)
                    if isinstance(attr, set):
                        return attr

        # Fallback: Check non-empty collections by instance type
        for attr_name in dir(memory_db):
            if attr_name.startswith("_") or attr_name.startswith("model_"):
                continue

            attr = getattr(memory_db, attr_name)
            if isinstance(attr, set) and attr:
                if any(isinstance(item, model_type) for item in attr):
                    return attr

        # Return empty set if not found (for models without collections)
        return set()

    def _get_model_type(self) -> type[Model]:
        """Extract the Model type parameter from the class hierarchy.

        Returns:
            type[Model]: The concrete type of Model used in the gateway.

        Raises:
            ValueError: If Model type cannot be determined.
        """
        # Check __orig_bases__ to get the generic type parameter
        for base in self.__class__.__orig_bases__:  # type: ignore[attr-defined]
            if hasattr(base, "__origin__") and base.__origin__ is FakeGateway:
                args = typing.get_args(base)
                if args:
                    return args[0]  # type: ignore[no-any-return]

        raise ValueError(f"Could not determine Model type for {self.__class__.__name__}")
