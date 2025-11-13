from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.application.ensure import ServiceInsuranceBase
from src.apps.hotel.rooms.application import exceptions


class RoomServiceInsurance(ServiceInsuranceBase):
    """Room service ensuring."""
    def __init__(
        self,
        gateway: RoomGatewayProto
    ) -> None:
        self._room = gateway

    async def room_exists(self, hotel_id: int, room_id: int) -> Room:
        room = await self._room.get_room(hotel_id, room_id)
        if room is None:
            raise exceptions.RoomNotFoundException
        return room
