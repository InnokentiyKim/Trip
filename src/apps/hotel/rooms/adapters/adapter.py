import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.adapters.adapter import FakeGateway, SQLAlchemyGateway


class RoomAdapter(SQLAlchemyGateway, RoomGatewayProto):
    async def list_rooms(self, hotel_id: uuid.UUID, **filters: Any) -> list[Room]:
        """
        Retrieve a list of rooms.

        Args:
            hotel_id (uuid.UUID): The ID of the hotel to filter rooms by.
            **filters: Additional filters to apply.

        Supported filters:
            - services: dict[str, bool]
            - price_from: Decimal
            - price_to: Decimal

        Returns:
            list[Room]: A list of rooms matching the criteria.
        """
        services = filters.get("services", None)
        price_from = filters.get("price_from", 0)
        price_to = filters.get("price_to", None)
        criteria = [Room.hotel_id == hotel_id]

        if services is not None:
            criteria.append(Room.services.op("@>")(services))
        if price_from:
            criteria.append(Room.price >= price_from)
        if price_to is not None:
            criteria.append(Room.price <= price_to)

        stmt = select(Room).filter(*criteria)
        row_result = await self.session.scalars(stmt)
        return list(row_result.all())

    async def get_room(self, room_id: uuid.UUID) -> Room | None:
        """
        Retrieve a room by its ID.

        Args:
            room_id (uuid.UUID): The ID of the room to retrieve.

        Returns:
            Room | None: The room if found, otherwise None.
        """
        room = await self.get_one_item(Room, id=room_id)
        return room

    async def add_room(
        self,
        hotel_id: uuid.UUID,
        owner: uuid.UUID,
        name: str,
        price: Decimal,
        quantity: int | None,
        description: str | None = None,
        services: dict[str, bool] | None = None,
        image_id: int | None = None,
    ) -> uuid.UUID | None:
        """
        Add a new room.

        Args:
            hotel_id (uuid.UUID): The ID of the hotel the room belongs to.
            owner (uuid.UUID): The ID of the room owner.
            name (str): The name of the room.
            price (Decimal): The price of the room.
            quantity (int | None): The quantity of rooms available.
            description (str | None): The description of the room.
            services (dict[str, bool] | None): The services offered in the room.
            image_id (int | None): The ID of the room's image.

        Returns:
            uuid.UUID | None: The ID of the newly added room, or None if addition failed
        """
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

    async def update_room(self, room: Room, **params: Any) -> uuid.UUID | None:
        """
        Update an existing room.

        Args:
            room (Room): The room instance to update.
            **params: The parameters to update.

        Returns:
            uuid.UUID | None: The ID of the updated room, or None if update failed.
        """
        room_id = room.id
        stmt = update(Room).where(Room.id == room_id).values(**params)
        try:
            await self.session.execute(stmt)
            return room_id
        except IntegrityError:
            return None

    async def delete_room(self, room: Room) -> None:
        """
        Delete a room by its ID.

        Args:
            room (Room): The room instance to delete.

        Returns:
            None
        """
        await self.delete_item(room)


class FakeRoomAdapter(FakeGateway[Room], RoomGatewayProto):
    async def list_rooms(self, hotel_id: uuid.UUID, **filters: Any) -> list[Room]:
        """Retrieve a list of rooms."""
        return [
            room
            for room in self._collection
            if room.hotel_id == hotel_id and all(getattr(room, k) == v for k, v in filters.items())
        ]

    async def get_room(self, room_id: uuid.UUID) -> Room | None:
        """Retrieve a room by its ID."""
        return next(
            (room for room in self._collection if room.id == room_id),
            None,
        )

    async def add_room(
        self,
        hotel_id: uuid.UUID,
        owner: uuid.UUID,
        name: str,
        price: Decimal,
        quantity: int | None,
        description: str | None = None,
        services: dict[str, bool] | None = None,
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
        return room.id

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
