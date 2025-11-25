from decimal import Decimal
from typing import Any

from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.adapters.adapter import SQLAlchemyGateway
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class RoomAdapter(SQLAlchemyGateway, RoomGatewayProto):
    async def list_rooms(self, hotel_id: int, **filters) -> list[Room]:
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

    async def get_room(self, hotel_id: int, room_id: int) -> Room | None:
        """Retrieve a room by its ID."""
        room = await self.get_one_item(Room, id=room_id, hotel_id=hotel_id)
        return room

    async def add_room(
        self,
        hotel_id: int,
        name: str,
        price: Decimal,
        quantity: int | None,
        description: str | None = None,
        services: dict | None = None,
        image_id: int | None = None,
    ) -> int | None:
        """Add a new room."""
        room = Room(
            hotel_id=hotel_id,
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

    async def update_room(self, room: Room, **params: dict[str, Any]) -> int | None:
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
