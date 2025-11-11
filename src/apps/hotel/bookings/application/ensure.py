from uuid import UUID
from src.apps.hotel.bookings.domain.model import Booking
from src.apps.hotel.bookings.application import exceptions
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.common.application.ensure import ServiceInsuranceBase
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum


class BookingServiceInsurance(ServiceInsuranceBase):
    """Booking service ensuring."""
    def __init__(
        self,
        gateway: BookingGatewayProto
    ) -> None:
        self._booking = gateway

    async def booking_exists(self, booking_id: UUID, user_id: int | UUID) -> Booking:
        booking = await self._booking.get_booking_by_id(booking_id, user_id=user_id)
        if booking is None:
            raise exceptions.BookingNotFoundException
        return booking

    async def active_booking_exists(self, booking_id: UUID, user_id: int | UUID) -> Booking:
        booking: Booking = await self._booking.get_booking_by_id(booking_id, user_id=user_id)
        active_statuses = [
            BookingStatusEnum.PENDING,
            BookingStatusEnum.CONFIRMED
        ]
        if booking and booking.status in active_statuses:
            return booking
        raise exceptions.BookingNotFoundException
