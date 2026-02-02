from dishka import AsyncContainer, Provider, Scope, provide, provide_all

from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.application.ensure import BookingServiceEnsurance
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.bookings.application.service import BookingService
from src.apps.hotel.hotels.adapters.adapter import HotelAdapter
from src.apps.hotel.hotels.application.ensure import HotelServiceEnsurance
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.rooms.adapters.adapter import RoomAdapter
from src.apps.hotel.rooms.application.ensure import RoomServiceEnsurance
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.application.service import RoomService
from src.common.domain.enums import GatewayTypeEnum


class ServiceProviders(Provider):
    """Register service providers."""

    scope = Scope.REQUEST

    services = provide_all(
        HotelService,
        HotelServiceEnsurance,
        RoomService,
        RoomServiceEnsurance,
        BookingService,
        BookingServiceEnsurance,
    )


class GatewayProviders(Provider):
    """Register hotel gateway providers."""

    scope = Scope.REQUEST

    # Register Hotel adapters
    _alchemy_hotels_adapter = provide(HotelAdapter)

    # Register Room adapters
    _alchemy_rooms_adapter = provide(RoomAdapter)

    # Register Booking adapter
    _alchemy_bookings_adapter = provide(BookingAdapter)

    @provide(provides=HotelGatewayProto)
    async def provide_hotel_gateway(self, request_container: AsyncContainer) -> HotelGatewayProto:
        """
        Provide an instance of HotelGatewayProto based on the configured gateway type.

        Uses container to retrieve only the selected implementation,
        which is instantiated on-demand with all dependencies auto-wired.

        Args:
            request_container: Dependency injection container.

        Returns:
            HotelGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(HotelAdapter)
        else:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")

    @provide(provides=RoomGatewayProto)
    async def provide_room_gateway(self, request_container: AsyncContainer) -> RoomGatewayProto:
        """
        Provide an instance of RoomGatewayProto based on the configured gateway type.

        Args:
            request_container: Dependency injection container.

        Returns:
            RoomGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(RoomAdapter)
        else:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")

    @provide(provides=BookingGatewayProto)
    async def provide_booking_gateway(self, request_container: AsyncContainer) -> BookingGatewayProto:
        """
        Provide an instance of BookingGatewayProto based on the configured gateway type.

        Args:
            request_container: Dependency injection container.

        Returns:
            BookingGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(BookingAdapter)
        else:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")


def get_hotel_providers() -> list[Provider]:
    """Get the list of hotel-related providers."""
    return [ServiceProviders(), GatewayProviders()]
