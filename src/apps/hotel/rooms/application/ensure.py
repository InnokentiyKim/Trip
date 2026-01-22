from uuid import UUID

from src.apps.hotel.rooms.application import exceptions
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.application.ensure import ServiceEnsuranceBase
from src.common.interfaces import CustomLoggerProto


class RoomServiceEnsurance(ServiceEnsuranceBase):
    """Room service ensuring."""

    def __init__(self, gateway: RoomGatewayProto, logger: CustomLoggerProto) -> None:
        self._room = gateway
        self._logger = logger

    async def room_exists(self, room_id: UUID) -> Room:
        """Ensure that a room exists by its ID."""
        room = await self._room.get_room(room_id)

        if room is None:
            self._logger.error("Room not found", room_id=room_id)
            raise exceptions.RoomNotFoundError

        return room
