from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.common.application.ensure import ServiceInsuranceBase
from src.apps.hotel.hotels.application import exceptions


class HotelServiceInsurance(ServiceInsuranceBase):
    """Hotel service ensuring."""
    def __init__(
        self,
        gateway: HotelGatewayProto
    ) -> None:
        self._hotel = gateway

    async def hotel_exists(self, hotel_id: int) -> Hotel:
        hotel = await self._hotel.get_hotel_by_id(hotel_id)
        if hotel is None:
            raise exceptions.HotelNotFoundException
        return hotel
