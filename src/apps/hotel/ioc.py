from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.hotels.adapters.adapter import HotelAdapter
from src.apps.hotel.rooms.adapters.adapter import RoomAdapter
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.config import Configs
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.bookings.application.service import BookingService
from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.rooms.application.service import RoomService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        HotelService,
        RoomService,
        BookingService,
    )


class GatewayProvider(Provider):

    scope = Scope.REQUEST

    @provide(HotelGatewayProto)
    def provide_hotels_gateway(self, session: AsyncSession, config: Configs) -> HotelGatewayProto:
        hotels_config = None
        return HotelAdapter(session=session)

    @provide(RoomGatewayProto)
    def provide_rooms_gateway(self, session: AsyncSession, config: Configs) -> RoomGatewayProto:
        rooms_config = None
        return RoomAdapter(session=session)

    @provide(BookingGatewayProto)
    def provide_bookings_gateway(self, session: AsyncSession, config: Configs) -> BookingGatewayProto:
        bookings_config = None
        return BookingAdapter(session=session)


def get_hotel_providers() -> list[Provider]:
    return [ServiceProvider(), GatewayProvider()]
