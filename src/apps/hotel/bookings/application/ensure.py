from uuid import UUID
from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.bookings.application import exceptions
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.common.application.ensure import ServiceInsuranceBase
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.common.interfaces import CustomLoggerProto


class BookingServiceInsurance(ServiceInsuranceBase):
    """Booking service ensuring."""

    def __init__(self, gateway: BookingGatewayProto, logger: CustomLoggerProto) -> None:
        self._booking = gateway
        self._logger = logger

    async def booking_exists(self, booking_id: UUID, user_id: int | UUID) -> Booking:
        booking = await self._booking.get_booking_by_id(booking_id, user_id=user_id)
        if booking is None:
            self._logger.error("Booking not found", booking_id=str(booking_id), user_id=str(user_id))
            raise exceptions.BookingNotFoundException
        return booking

    async def active_booking_exists(
        self, booking_id: UUID, user_id: int | UUID
    ) -> Booking:
        booking: Booking | None = await self._booking.get_booking_by_id(
            booking_id, user_id=user_id
        )
        active_statuses = [BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED]
        if booking and booking.status in active_statuses:
            return booking

        self._logger.error("Active booking not found", booking_id=booking_id, user_id=user_id)
        raise exceptions.BookingNotFoundException
