from src.apps.hotel.hotels.domain import commands
from src.apps.hotel.hotels.application import exceptions
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.hotels.domain.model import Hotel
from src.common.application.service import ServiceBase


class HotelService(ServiceBase):
    def __init__(
        self,
        gateway: HotelGatewayProto
    ) -> None:
        self._adapter = gateway

    async def list_hotels(self, cmd: commands.ListHotelsCommand) -> list[Hotel]:
        params = cmd.model_dump(exclude_unset=True)
        hotels = await self._adapter.get_hotels(**params)
        return hotels

    async def get_hotel(self, cmd: commands.GetHotelCommand) -> Hotel:
        hotel = await self._adapter.get_hotel_by_id(cmd.hotel_id)
        if hotel is None:
            raise exceptions.HotelNotFoundException
        return hotel

    async def create_hotel(self, cmd: commands.CreateHotelCommand) -> int | None:
        params = cmd.model_dump(exclude_unset=True)

        hotel = Hotel(
            name=params.pop("name"),
            location=params.pop("location"),
            rooms_quantity=params.pop("rooms_quantity"),
            owner=params.pop("owner"),
        )
        for key, value in params.items():
            setattr(hotel, key, value)
        new_hotel_id = await self._adapter.add_hotel(hotel)
        if not new_hotel_id:
            raise exceptions.HotelAlreadyExistsException
        return new_hotel_id

    async def update_hotel(self, cmd: commands.UpdateHotelCommand) -> int | None:
        params = cmd.model_dump(exclude={"user_id", "hotel_id"}, exclude_unset=True)
        hotel_id = await self._adapter.update_hotel(cmd.user_id, cmd.hotel_id, **params)
        if hotel_id is None:
            raise exceptions.HotelNotFoundException
        return hotel_id

    async def delete_hotel(self, cmd: commands.DeleteHotelCommand) -> int | None:
        hotel_id = await self._adapter.delete_hotel(cmd.user_id, cmd.hotel_id)
        if hotel_id is None:
            raise exceptions.HotelNotFoundException
        return hotel_id
