from datetime import date
from typing import Any
from uuid import UUID

from apps.hotel.bookings.application.exceptions import BookingNotFoundException, BookingProcessingErrorException
from apps.hotel.bookings.domain.enums import BookingStatusEnum
from common.utils.dependency import SessionDependency
from src.apps.hotel.bookings.domain.model import Booking
from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.common.application.service import ServiceBase


class BookingService(ServiceBase):
    def __init__(
        self,
        booking: BookingAdapter
    ) -> None:
        self._booking = booking

    async def get_booking(self, user_id: int, booking_id: UUID) -> Booking:
        booking = await self._booking.get_booking_by_id(booking_id, user_id=user_id)
        if booking is None:
            raise BookingNotFoundException
        return booking

    async def get_bookings_by_status(self, user_id: int, status: BookingStatusEnum) -> list[Booking]:
        bookings = await self._booking.get_bookings(status=status, user_id=user_id)
        if not bookings:
            raise BookingNotFoundException
        return bookings

    async def get_bookings(self, user_id: int, **filters) -> list[Booking]:
        bookings = await self._booking.get_bookings(user_id=user_id, **filters)
        return bookings

    async def delete_booking(self, user_id: int, booking_id: UUID, **filters) -> UUID:
        result = await self._booking.delete_booking(user_id, booking_id, **filters)
        return result

    async def create_booking(self, user_id: int, room_id: int, date_from: date, date_to: date) -> int | None:
        result = await self._booking.add_booking(user_id, room_id, date_from, date_to)
        return result

    async def update_booking_status(self, user_id: int, booking_id: UUID, status: BookingStatusEnum) -> UUID:
        updated = await self._booking.update_booking(user_id, booking_id, status=status)
        if not updated:
            raise BookingProcessingErrorException
        return updated

    async def cancel_active_booking(self, user_id: int, booking_id: UUID) -> UUID:
        await self._booking.update_booking(user_id, booking_id, only_active=True)
        return booking_id
