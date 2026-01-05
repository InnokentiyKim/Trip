import uuid
from abc import abstractmethod
from decimal import Decimal
from typing import Any

from src.apps.hotel.rooms.domain.models import Room
from src.common.interfaces import GatewayProto


class RoomGatewayProto(GatewayProto):
    @abstractmethod
    async def list_rooms(self, hotel_id: uuid.UUID, **filters) -> list[Room]:
        """Retrieve a list of rooms."""
        ...

    @abstractmethod
    async def get_room(self, room_id: uuid.UUID) -> Room | None:
        """Retrieve a room by its ID."""
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def update_room(self, room: Room, **params: dict[str, Any]) -> uuid.UUID | None:
        """Update an existing room."""
        ...

    @abstractmethod
    async def delete_room(self, room: Room) -> uuid.UUID | None:
        """Delete a room by its ID."""
        ...
