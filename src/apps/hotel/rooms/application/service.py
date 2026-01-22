from uuid import UUID

from src.apps.hotel.hotels.application.ensure import HotelServiceEnsurance
from src.apps.hotel.rooms.application import exceptions
from src.apps.hotel.rooms.application.ensure import RoomServiceEnsurance
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain import commands
from src.apps.hotel.rooms.domain.models import Room
from src.common.application.service import ServiceBase
from src.common.interfaces import CustomLoggerProto


class RoomService(ServiceBase):
    def __init__(
        self,
        hotel_ensure: HotelServiceEnsurance,
        room_gateway: RoomGatewayProto,
        logger: CustomLoggerProto,
    ) -> None:
        self._room_adapter = room_gateway
        self._logger = logger
        self._hotel_ensure = hotel_ensure
        self._room_ensure = RoomServiceEnsurance(room_gateway, logger)
        super().__init__()

    async def list_rooms(self, cmd: commands.ListRoomsCommand) -> list[Room]:
        """List rooms for a specific hotel with optional filters."""
        params = cmd.model_dump(exclude={"hotel_id"}, exclude_unset=True, exclude_none=True)
        rooms = await self._room_adapter.list_rooms(cmd.hotel_id, **params)

        return rooms

    async def get_room(self, cmd: commands.GetRoomCommand) -> Room:
        """Get details of a specific room by its ID."""
        room = await self._room_adapter.get_room(cmd.room_id)
        if room is None:
            self._logger.error("Room not found", room_id=cmd.room_id)
            raise exceptions.RoomNotFoundError
        return room

    async def add_room(self, cmd: commands.AddRoomCommand) -> UUID:
        """Add a new room to a hotel."""
        hotel = await self._hotel_ensure.users_hotel_exists(cmd.user_id, cmd.hotel_id)

        room_id = await self._room_adapter.add_room(
            hotel.id,
            cmd.user_id,
            cmd.name,
            cmd.price,
            cmd.quantity,
            cmd.description,
            cmd.services,
            cmd.image_id,
        )

        if room_id is None:
            self._logger.error("Room already exists", hotel_id=cmd.hotel_id, name=cmd.name)
            raise exceptions.RoomAlreadyExistsError

        self._logger.info("New room successfully added", hotel_id=cmd.hotel_id, room_id=room_id)
        return room_id

    async def update_room(self, cmd: commands.UpdateRoomCommand) -> UUID:
        """Update an existing room's details."""
        room = await self._room_ensure.room_exists(cmd.room_id)

        updating_params = cmd.model_dump(
            exclude={"room_id", "user_id"},
            exclude_unset=True,
            exclude_none=True,
        )

        updated_room_id = await self._room_adapter.update_room(room, **updating_params)

        if updated_room_id is None:
            self._logger.error("Room cannot be updated", user_id=room.owner, room_id=cmd.room_id)
            raise exceptions.RoomCannotBeUpdatedError

        self._logger.info("Room successfully updated", user_id=room.owner, room_id=cmd.room_id)
        return updated_room_id

    async def delete_room(self, cmd: commands.DeleteRoomCommand) -> None:
        """Delete an existing room."""
        room = await self._room_ensure.room_exists(cmd.room_id)

        await self._room_adapter.delete_room(room)
        self._logger.info("Room successfully deleted", room_id=cmd.room_id)
