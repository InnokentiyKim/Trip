import uuid
from decimal import Decimal
from typing import Any

from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.adapters.adapter import SQLAlchemyGateway, FakeGateway
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class RoomAdapter(SQLAlchemyGateway, RoomGatewayProto):
    async def list_rooms(self, hotel_id: uuid.UUID, **filters) -> list[Room]:
        """Retrieve a list of rooms."""
        services = filters.get("services", [])
        price_from = filters.get("price_from", 0)
        price_to = filters.get("price_to", None)
        criteria = [Room.price >= price_from]
        if services:
            criteria.append(Room.services.in_(services))
        if price_to is not None:
            criteria.append(Room.price <= price_to)
        stmt = select(Room).filter(*criteria)
        row_result = await self.session.scalars(stmt)
        return list(row_result.all())

    async def get_room(self, hotel_id: uuid.UUID, room_id: uuid.UUID) -> Room | None:
        """Retrieve a room by its ID."""
        room = await self.get_one_item(Room, id=room_id, hotel_id=hotel_id)
        return room

    async def add_room(
        self,
        hotel_id: uuid.UUID,
        owner: uuid.UUID,
        name: str,
        price: Decimal,
        quantity: int | None,
        description: str | None = None,
        services: dict | None = None,
        image_id: int | None = None,
    ) -> uuid.UUID | None:
        """Add a new room."""
        room = Room(
            hotel_id=hotel_id,
            owner=owner,
            name=name,
            price=price,
            description=description,
            services=services,
            image_id=image_id,
        )

        if quantity is not None:
            room.quantity = quantity

        self.session.add(room)
        try:
            await self.session.commit()
            return room.id
        except IntegrityError:
            return None

    async def update_room(self, room: Room, **params: dict[str, Any]) -> uuid.UUID | None:
        """Update an existing room."""
        for key, value in params.items():
            setattr(room, key, value)
        try:
            await self.session.commit()
            return room.id
        except IntegrityError:
            return None

    async def delete_room(self, room: Room) -> None:
        """Delete a room by its ID."""
        await self.delete_item(room)


class FakeRoomAdapter(FakeGateway[Room], RoomGatewayProto):
    async def list_rooms(self, hotel_id: int, **filters) -> list[Room]:
        """Retrieve a list of rooms."""
        return [
            room for room in self._collection if room.hotel_id == hotel_id
            and all(getattr(room, k) == v for k, v in filters.items())
        ]

    async def get_room(self, hotel_id: int, room_id: int) -> Room | None:
        """Retrieve a room by its ID."""
        return next((room for room in self._collection if room.id == room_id and room.hotel_id == hotel_id), None)

    async def add_room(
        self,
        hotel_id: uuid.UUID,
        owner: uuid.UUID,
        name: str,
        price: Decimal,
        quantity: int | None,
        description: str | None = None,
        services: dict | None = None,
        image_id: int | None = None,
    ) -> uuid.UUID | None:
        """Add a new room."""
        room = Room(
            hotel_id=hotel_id,
            owner=owner,
            name=name,
            price=price,
            description=description,
            services=services,
            image_id=image_id,
        )

        self._collection.add(room)

    async def update_room(self, room: Room, **params: dict[str, Any]) -> uuid.UUID | None:
        """Update an existing room."""
        for key, value in params.items():
            setattr(room, key, value)

        self._collection.discard(room)
        self._collection.add(room)

        return room.id or None

    async def delete_room(self, room: Room) -> None:
        """Delete a room by its ID."""
        self._collection.discard(room)
