from src.apps.hotel.rooms.domain.commands import AddRoomCommand
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.model import Room
from src.common.adapters.adapter import SQLAlchemyGateway
from src.common.utils.dependency import SessionDependency


class RoomAdapter(SQLAlchemyGateway, RoomGatewayProto):
    async def get_rooms(self, hotel_id: int, **filters) -> list[Room]:
        """Retrieve a list of rooms."""
        rooms = await self.get_items_list(SessionDependency, 'Room', hotel_id=hotel_id, **filters)
        return rooms

    async def get_room(self, hotel_id: int, room_id: int) -> Room | None:
        """Retrieve a room by its ID."""
        room = await self.get_one_item(SessionDependency, 'Room', id=room_id, hotel_id=hotel_id)
        return room

    async def add_room(self, cmd: AddRoomCommand) -> None:
        """Add a new room."""
        room = Room.from_dict(**cmd.model_dump(exclude_none=True))
        await self.add_item(SessionDependency, room)

    async def update_room(self, hotel_id: int, room_id: int, **params) -> int | None:
        """Update an existing room."""
        hotel = await self.get_one_item(SessionDependency, 'Hotel', id=hotel_id)
        if not hotel:
            return None
        room = await self.get_one_item(SessionDependency, 'Room', id=room_id, hotel_id=hotel_id)
        if not room:
            return None
        updated_room = room.from_dict(params)
        await self.add_item(SessionDependency, updated_room)
        return room.id

    async def delete_room(self, hotel_id: int, room_id: int) -> int | None:
        """Delete a room by its ID."""
        room = await self.get_one_item(SessionDependency, 'Room', id=room_id, hotel_id=hotel_id)
        if not room:
            return None
        await self.delete_item(SessionDependency, room)
        return room_id
