from src.apps.hotel.hotels.domain import commands
from src.apps.hotel.hotels.application import exceptions
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.hotels.domain.models import Hotel
from src.common.application.service import ServiceBase
from src.apps.hotel.hotels.application.ensure import HotelServiceInsurance


class HotelService(ServiceBase):
    def __init__(
        self,
        gateway: HotelGatewayProto
    ) -> None:
        self._adapter = gateway
        self._ensure = HotelServiceInsurance(gateway)

    async def list_hotels(self, cmd: commands.ListHotelsCommand) -> list[Hotel]:
        params = cmd.model_dump(exclude_unset=True)
        hotels = await self._adapter.get_hotels(**params)
        return hotels

    async def get_hotel(self, cmd: commands.GetHotelCommand) -> Hotel:
        hotel = await self._ensure.hotel_exists(cmd.hotel_id)
        return hotel

    async def create_hotel(self, cmd: commands.CreateHotelCommand) -> int:
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
        if new_hotel_id is None:
            raise exceptions.HotelAlreadyExistsException
        return new_hotel_id

    async def update_hotel(self, cmd: commands.UpdateHotelCommand) -> int:
        hotel = await self._ensure.hotel_exists(cmd.hotel_id)
        params = cmd.model_dump(exclude={"hotel_id"}, exclude_unset=True)
        is_updated = await self._adapter.update_hotel(hotel, **params)
        if is_updated is None:
            raise exceptions.HotelCannotBeUpdatedException
        return is_updated

    async def delete_hotel(self, cmd: commands.DeleteHotelCommand) -> None:
        hotel = await self._ensure.hotel_exists(cmd.hotel_id)
        await self._adapter.delete_hotel(hotel)
