from datetime import date
from typing import Any
from uuid import UUID

from apps.hotel.bookings.application.exceptions import BookingNotFoundException, BookingProcessingErrorException
from apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.apps.hotel.bookings.domain.model import Bookings
from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.common.application.service import ServiceBase


class BookingService(ServiceBase):
    def __init__(
        self,
        booking: BookingAdapter
    ) -> None:
        self._booking = booking

    async def get_booking_by_id(self, booking_id: int, **filters: Any) -> Bookings:
        booking = await self._booking.get_booking_by_id(booking_id, **filters)
        if booking is None:
            raise BookingNotFoundException
        return booking

    async def get_bookings_by_status(self, status: BookingStatusEnum, **filters) -> list[Bookings]:
        bookings = await self.get_bookings(status=status, **filters)
        if bookings is None:
            raise BookingNotFoundException
        return bookings

    async def get_bookings(self, **filters) -> list[Bookings]:
        bookings = await self._booking.get_bookings(**filters)
        return bookings

    async def delete_booking(self, booking_id: UUID) -> UUID:
        result = await self._booking.delete_booking(booking_id)
        return result

    async def add_booking(self, user_id: int, room_id: int, date_from: date, date_to: date) -> int | None:
        result = await self._booking.add_booking(user_id, room_id, date_from, date_to)
        return result

    async def update_booking_status(self, user_id: int, booking_id: int, status: BookingStatusEnum) -> UUID:
        booking = await self.get_booking_by_id(booking_id, user_id=user_id)
        if not booking:
            raise BookingNotFoundException
        booking.status = status
        updated = await self._booking.update_booking(booking)
        if not updated:
            raise BookingProcessingErrorException
        return updated

    async def cancel_active_booking(self, user_id: int, booking_id: int) -> UUID:
        active_bookings = await self._booking.get_active_bookings(user_id=user_id, booking_id=booking_id)
        if not active_bookings:
            raise BookingNotFoundException
        booking = active_bookings[0]
        booking.status = BookingStatusEnum.CANCELLED
        updated = await self._booking.update_booking(booking)
        if not updated:
            raise BookingProcessingErrorException
        return updated
