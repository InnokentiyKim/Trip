from abc import abstractmethod
from decimal import Decimal
from typing import Any

from src.apps.hotel.rooms.domain.commands import AddRoomCommand
from src.apps.hotel.rooms.domain.model import Room
from src.common.interfaces import GatewayProto


class RoomGatewayProto(GatewayProto):
    @abstractmethod
    async def list_rooms(self, hotel_id: int, **filters) -> list[Room]:
        """Retrieve a list of rooms."""
        ...

    @abstractmethod
    async def get_room(self, hotel_id: int, room_id: int) -> Room| None:
        """Retrieve a room by its ID."""
        ...

    @abstractmethod
    async def add_room(self, hotel_id: int, name: str, price: Decimal, quantity: int | None,
        description: str | None = None, services: dict | None = None, image_id: int | None = None
    ) -> None:
        """Add a new room."""
        ...

    @abstractmethod
    async def update_room(self, hotel_id: int, room_id: int, **params: dict[str, Any]) -> int | None:
        """Update an existing room."""
        ...

    @abstractmethod
    async def delete_room(self, hotel_id: int, room_id: int) -> int | None:
        """Delete a room by its ID."""
        ...
