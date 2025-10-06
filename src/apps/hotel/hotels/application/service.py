from apps.hotel.hotels.application.commands import CreateHotelCommand
from apps.hotel.hotels.application.exceptions import HotelNotFoundException, HotelAlreadyExistsException
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.hotels.domain.model import Hotel
from src.common.application.service import ServiceBase


class HotelService(ServiceBase):
    def __init__(
        self,
        hotel: HotelGatewayProto
    ) -> None:
        self._hotel = hotel

    async def get_hotels(self, **filters) -> list[Hotel]:
        hotels = await self._hotel.get_hotels(**filters)
        if not hotels:
            raise HotelNotFoundException
        return hotels

    async def get_hotel(self, hotel_id: int) -> Hotel:
        hotel = await self._hotel.get_hotel_by_id(hotel_id)
        if hotel is None:
            raise HotelNotFoundException
        return hotel

    async def create_hotel(self, cmd: CreateHotelCommand) -> int | None:
        hotel = Hotel(
            name=cmd.name,
            location=cmd.location,
            rooms_quantity=cmd.rooms_quantity,
            owner=cmd.owner
        )
        if cmd.services:
            hotel.services = cmd.services
        if cmd.image_id:
            hotel.image_id = cmd.image_id
        new_hotel_id = await self._hotel.add_hotel(hotel)
        if not new_hotel_id:
            raise HotelAlreadyExistsException
        return new_hotel_id

    async def update_hotel(self, user_id: int, hotel_id: int, **params) -> None:
        await self._hotel.update_hotel(user_id, hotel_id, **params)

    async def delete_hotel(self, user_id: int, hotel_id: int) -> None:
        await self._hotel.delete_hotel(user_id, hotel_id)
