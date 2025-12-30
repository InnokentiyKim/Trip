from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.application.ensure import ServiceEnsuranceBase
from src.apps.hotel.rooms.application import exceptions
from src.common.interfaces import CustomLoggerProto


class RoomServiceInsurance(ServiceEnsuranceBase):
    """Room service ensuring."""

    def __init__(self, gateway: RoomGatewayProto, logger: CustomLoggerProto) -> None:
        self._room = gateway
        self._logger = logger

    async def room_exists(self, hotel_id: int, room_id: int) -> Room:
        room = await self._room.get_room(hotel_id, room_id)
        if room is None:
            self._logger.error("Room not found", hotel_id=hotel_id, room_id=room_id)
            raise exceptions.RoomNotFoundException
        return room
