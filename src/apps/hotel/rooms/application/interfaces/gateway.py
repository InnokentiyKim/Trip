from abc import abstractmethod

from src.apps.hotel.rooms.domain.commands import AddRoomCommand
from src.apps.hotel.rooms.domain.model import Room
from src.common.interfaces import GatewayProto


class RoomGatewayProto(GatewayProto):
    @abstractmethod
    async def get_rooms(self, hotel_id: int, **filters) -> list[Room]:
        """Retrieve a list of rooms."""
        ...

    @abstractmethod
    async def get_room(self, hotel_id: int, room_id: int) -> Room| None:
        """Retrieve a room by its ID."""
        ...

    @abstractmethod
    async def add_room(self, cmd: AddRoomCommand) -> None:
        """Add a new room."""
        ...

    @abstractmethod
    async def update_room(self, hotel_id: int, room_id: int, **params) -> int | None:
        """Update an existing room."""
        ...

    @abstractmethod
    async def delete_room(self, hotel_id: int, room_id: int) -> int:
        """Delete a room by its ID."""
        ...
