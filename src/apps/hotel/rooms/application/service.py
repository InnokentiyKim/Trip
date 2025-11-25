from src.apps.hotel.rooms.application.ensure import RoomServiceInsurance
from src.apps.hotel.rooms.domain import commands
from src.apps.hotel.rooms.application import exceptions
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.application.service import ServiceBase


class RoomService(ServiceBase):
    def __init__(
        self,
        # hotel_gateway: HotelGatewayProto,
        room_gateway: RoomGatewayProto,
    ) -> None:
        self._room_adapter = room_gateway
        # self._hotel_ensure = HotelServiceInsurance(hotel_gateway)
        self._room_ensure = RoomServiceInsurance(room_gateway)

    async def list_rooms(self, cmd: commands.ListRoomsCommand) -> list[Room]:
        params = cmd.model_dump(exclude={"hotel_id"}, exclude_unset=True)
        rooms = await self._room_adapter.list_rooms(cmd.hotel_id, **params)
        return rooms

    async def get_room(self, cmd: commands.GetRoomCommand) -> Room:
        room = await self._room_adapter.get_room(cmd.hotel_id, cmd.room_id)
        if room is None:
            raise exceptions.RoomNotFoundException
        return room

    async def add_room(self, cmd: commands.AddRoomCommand) -> int | None:
        # hotel = await self._hotel_ensure.users_hotel_exists(cmd.user_id, cmd.hotel_id)
        room_id = await self._room_adapter.add_room(
            cmd.hotel_id,
            cmd.name,
            cmd.price,
            cmd.quantity,
            cmd.description,
            cmd.services,
            cmd.image_id,
        )
        if room_id is None:
            raise exceptions.RoomAlreadyExistsException
        return room_id

    async def update_room(self, cmd: commands.UpdateRoomCommand) -> int:
        # hotel = await self._hotel_ensure.users_hotel_exists(cmd.user_id, cmd.hotel_id)
        room = await self._room_ensure.room_exists(cmd.hotel_id, cmd.room_id)

        updating_params = cmd.model_dump(
            exclude={"hotel_id", "room_id"}, exclude_unset=True
        )
        updated_room_id = await self._room_adapter.update_room(room, **updating_params)
        if updated_room_id is None:
            raise exceptions.RoomCannotBeUpdatedException
        return updated_room_id

    async def delete_room(self, cmd: commands.DeleteRoomCommand) -> None:
        # hotel = await self._hotel_ensure.users_hotel_exists(cmd.user_id, cmd.hotel_id)
        room = await self._room_ensure.room_exists(cmd.hotel_id, cmd.room_id)
        await self._room_adapter.delete_room(room)
