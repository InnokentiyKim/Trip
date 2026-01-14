from dishka import Provider, Scope, provide, provide_all, AsyncContainer

from src.apps.hotel.bookings.adapters.adapter import BookingAdapter, FakeBookingAdapter
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.config import HotelGatewayEnum
from src.apps.hotel.hotels.adapters.adapter import HotelAdapter, FakeHotelAdapter
from src.apps.hotel.hotels.application.ensure import HotelServiceEnsurance
from src.apps.hotel.rooms.adapters.adapter import RoomAdapter, FakeRoomAdapter
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.bookings.application.service import BookingService
from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.rooms.application.service import RoomService
from src.config import Configs


class ServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        HotelService,
        HotelServiceEnsurance,
        RoomService,
        BookingService,
    )


class GatewayProviders(Provider):
    scope = Scope.REQUEST

    # Register Hotel adapters
    _alchemy_hotels_adapter = provide(HotelAdapter)
    _memory_hotels_adapter = provide(FakeHotelAdapter)

    # Register Room adapters
    _alchemy_rooms_adapter = provide(RoomAdapter)
    _memory_rooms_adapter = provide(FakeRoomAdapter)

    # Register Booking adapter
    _alchemy_bookings_adapter = provide(BookingAdapter)
    _memory_bookings_adapter = provide(FakeBookingAdapter)

    @provide(provides=HotelGatewayProto)
    async def provide_hotel_gateway(self, config: Configs, request_container: AsyncContainer) -> HotelGatewayProto:
        """
        Provide an instance of HotelGatewayProto based on the configured gateway type.

        Uses container to retrieve only the selected implementation,
        which is instantiated on-demand with all dependencies auto-wired.

        Args:
            config: Application configuration (auto-injected).
            request_container: Dependency injection container.

        Returns:
            HotelGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = config.hotels.hotel.gateway

        if gateway_type == HotelGatewayEnum.ALCHEMY:
            return await request_container.get(HotelAdapter)
        elif gateway_type == HotelGatewayEnum.MEMORY:
            return await request_container.get(FakeHotelAdapter)
        else:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")

    @provide(provides=RoomGatewayProto)
    async def provide_room_gateway(self, config: Configs, request_container: AsyncContainer) -> RoomGatewayProto:
        """
        Provide an instance of RoomGatewayProto based on the configured gateway type.

        Args:
            config: Application configuration (auto-injected).
            request_container: Dependency injection container.

        Returns:
            RoomGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = config.hotels.room.gateway

        if gateway_type == HotelGatewayEnum.ALCHEMY:
            return await request_container.get(RoomAdapter)
        elif gateway_type == HotelGatewayEnum.MEMORY:
            return await request_container.get(FakeRoomAdapter)
        else:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")

    @provide(provides=BookingGatewayProto)
    async def provide_booking_gateway(self, config: Configs, request_container: AsyncContainer) -> BookingGatewayProto:
        """
        Provide an instance of BookingGatewayProto based on the configured gateway type.

        Args:
            config: Application configuration (auto-injected).
            request_container: Dependency injection container.

        Returns:
            BookingGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = config.hotels.booking.gateway

        if gateway_type == HotelGatewayEnum.ALCHEMY:
            return await request_container.get(BookingAdapter)
        elif gateway_type == HotelGatewayEnum.MEMORY:
            return await request_container.get(FakeBookingAdapter)
        else:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")


def get_hotel_providers() -> list[Provider]:
    return [ServiceProviders(), GatewayProviders()]
