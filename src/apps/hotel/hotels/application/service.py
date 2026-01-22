from uuid import UUID

from src.apps.hotel.hotels.application import exceptions
from src.apps.hotel.hotels.application.ensure import HotelServiceEnsurance
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.hotels.domain import commands
from src.apps.hotel.hotels.domain.models import Hotel
from src.common.application.service import ServiceBase
from src.common.interfaces import CustomLoggerProto


class HotelService(ServiceBase):
    def __init__(self, gateway: HotelGatewayProto, logger: CustomLoggerProto) -> None:
        self._adapter = gateway
        self._logger = logger
        self._ensure = HotelServiceEnsurance(gateway, logger)

    async def list_hotels(self, cmd: commands.ListHotelsCommand) -> list[Hotel]:
        """List hotels with optional filters."""
        params = cmd.model_dump(exclude_unset=True)
        hotels = await self._adapter.get_hotels(**params)
        return hotels

    async def get_hotel(self, cmd: commands.GetHotelCommand) -> Hotel:
        """Get details of a specific hotel by its ID."""
        hotel = await self._ensure.hotel_exists(cmd.hotel_id)
        return hotel

    async def create_hotel(self, cmd: commands.CreateHotelCommand) -> UUID:
        """Create a new hotel."""
        hotel = Hotel(
            name=cmd.name,
            location=cmd.location,
            rooms_quantity=cmd.rooms_quantity,
            owner=cmd.owner,
            services=cmd.services,
            image_id=cmd.image_id,
        )
        if cmd.is_active:
            hotel.is_active = cmd.is_active

        new_hotel_id = await self._adapter.add(hotel)
        if new_hotel_id is None:
            self._logger.error(
                "Hotel creation failed, hotel already exists",
                name=cmd.name,
                location=cmd.location,
            )
            raise exceptions.HotelAlreadyExistsError

        self._logger.info(
            "New hotel successfully created",
            hotel_id=new_hotel_id,
            owner=str(cmd.owner),
        )
        return new_hotel_id

    async def update_hotel(self, cmd: commands.UpdateHotelCommand) -> UUID:
        """Update an existing hotel's information."""
        hotel = await self._ensure.hotel_exists(cmd.hotel_id)
        params = cmd.model_dump(exclude={"hotel_id"}, exclude_unset=True, exclude_none=True)
        is_updated = await self._adapter.update_hotel(hotel, **params)
        if is_updated is None:
            self._logger.error("Hotel update failed", hotel_id=cmd.hotel_id)
            raise exceptions.HotelCannotBeUpdatedError

        self._logger.info("Hotel's info successfully updated", hotel_id=cmd.hotel_id)
        return is_updated

    async def delete_hotel(self, cmd: commands.DeleteHotelCommand) -> None:
        """Delete a hotel by its ID."""
        hotel = await self._ensure.hotel_exists(cmd.hotel_id)

        await self._adapter.delete_hotel(hotel)
        self._logger.info("Hotel successfully deleted", hotel_id=cmd.hotel_id)
