from src.apps.hotel.hotels.application.exceptions import HotelNotFoundException
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.rooms.domain import commands
from src.apps.hotel.rooms.application import exceptions
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.model import Room
from src.common.application.service import ServiceBase


class RoomService(ServiceBase):
    def __init__(
        self,
        room_gateway: RoomGatewayProto,
        hotel_gateway: HotelGatewayProto,
    ) -> None:
        self._room_adapter = room_gateway
        self._hotel_adapter = hotel_gateway

    async def list_rooms(self, cmd: commands.ListRoomsCommand) -> list[Room]:
        params = cmd.model_dump(exclude={'hotel_id'}, exclude_unset=True)
        rooms = await self._room_adapter.list_rooms(cmd.hotel_id, **params)
        return rooms

    async def get_room(self, cmd: commands.GetRoomCommand) -> Room:
        room = await self._room_adapter.get_room(cmd.hotel_id, cmd.room_id)
        if room is None:
            raise exceptions.RoomNotFoundException
        return room

    async def add_room(self, cmd: commands.AddRoomCommand) -> int | None:
        hotel = await self._hotel_adapter.get_hotel_by_id(cmd.hotel_id)
        if hotel is None:
            raise HotelNotFoundException
        result = await self._room_adapter.add_room(
            cmd.hotel_id, cmd.name, cmd.price, cmd.quantity, cmd.description, cmd.services, cmd.image_id
        )
        if result is None:
            raise exceptions.RoomNotFoundException
        return result

    async def update_room(self, cmd: commands.UpdateRoomCommand, **params) -> int:
        updated_room = await self._room_adapter.update_room(cmd.hotel_id, cmd.room_id, **params)
        if updated_room is None:
            raise exceptions.RoomNotFoundException
        return updated_room

    async def delete_room(self, cmd: commands.DeleteRoomCommand) -> int:
        deleted_room = await self._room_adapter.delete_room(cmd.hotel_id, cmd.room_id)
        if deleted_room is None:
            raise exceptions.RoomNotFoundException
        return deleted_room
