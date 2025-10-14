from src.apps.hotel.hotels.application.exceptions import HotelNotFoundException
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.rooms.domain.commands import AddRoomCommand, UpdateRoomCommand, DeleteRoomCommand
from src.apps.hotel.rooms.application.exceptions import RoomNotFoundException
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.model import Room
from src.common.application.service import ServiceBase


class RoomService(ServiceBase):
    def __init__(
        self,
        rooms: RoomGatewayProto,
        hotel: HotelGatewayProto,
    ) -> None:
        self._rooms = rooms
        self._hotel = hotel

    async def get_rooms(self, hotel_id: int, **filters) -> list[Room]:
        rooms = await self._rooms.get_rooms(hotel_id, **filters)
        return rooms

    async def get_room(self, hotel_id: int, room_id: int) -> Room:
        room = await self._rooms.get_room(hotel_id, room_id)
        if room is None:
            raise RoomNotFoundException
        return room

    async def add_room(self, cmd: AddRoomCommand) -> None:
        hotel = await self._hotel.get_hotel_by_id(cmd.hotel_id)
        if hotel is None:
            raise HotelNotFoundException
        await self._rooms.add_room(cmd)

    async def update_room(self, cmd: UpdateRoomCommand, **params) -> int:
        updated_room = await self._rooms.update_room(cmd.hotel_id, cmd.room_id, **params)
        if updated_room is None:
            raise RoomNotFoundException
        return updated_room

    async def delete_room(self, cmd: DeleteRoomCommand) -> int:
        deleted_room = await self._rooms.delete_room(cmd.hotel_id, cmd.room_id)
        if deleted_room is None:
            raise RoomNotFoundException
        return deleted_room
