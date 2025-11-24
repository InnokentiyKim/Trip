from dishka import Provider, Scope, provide, provide_all, AsyncContainer

from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.hotels.adapters.adapter import HotelAdapter
from src.apps.hotel.rooms.adapters.adapter import RoomAdapter
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.bookings.application.service import BookingService
from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.rooms.application.service import RoomService


class ServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        HotelService,
        RoomService,
        BookingService,
    )


class GatewayProviders(Provider):

    scope = Scope.REQUEST

    _hotels_adapter = provide(HotelAdapter)
    _rooms_adapter = provide(RoomAdapter)
    _bookings_adapter = provide(BookingAdapter)

    @provide(provides=HotelGatewayProto)
    async def provide_hotel_gateway(self, request_container: AsyncContainer) -> HotelGatewayProto:
        """"""
        return await request_container.get(HotelAdapter)

    @provide(provides=RoomGatewayProto)
    async def provide_room_gateway(self, request_container: AsyncContainer) -> RoomGatewayProto:
        """"""
        return await request_container.get(RoomAdapter)

    @provide(provides=BookingGatewayProto)
    async def provide_booking_gateway(self, request_container: AsyncContainer) -> BookingGatewayProto:
        """"""
        return await request_container.get(BookingAdapter)



def get_hotel_providers() -> list[Provider]:
    return [ServiceProviders(), GatewayProviders()]
