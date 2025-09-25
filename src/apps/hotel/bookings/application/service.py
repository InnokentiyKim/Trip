from datetime import date
from typing import Any

from apps.hotel.bookings.application.exception import BookingNotFoundException
from src.apps.hotel.bookings.domain.model import Bookings
from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.common.application.service import ServiceBase


class BookingService(ServiceBase):
    def __init__(
        self,
        booking: BookingAdapter
    ) -> None:
        self._booking = booking

    async def get_booking(self, booking_id: int, **filters: Any) -> Bookings:
        booking = await self._booking.get_booking_by_id(booking_id, **filters)
        if booking is None:
            raise BookingNotFoundException
        return booking

    async def get_bookings(self, **filters) -> list[Bookings]:
        bookings = await self._booking.get_bookings(**filters)
        return bookings

    async def delete_booking(self, booking_id: int) -> int:
        result = await self._booking.delete_booking(booking_id)
        return result

    async def add_booking(self, user_id: int, room_id: int, date_from: date, date_to: date) -> int | None:
        result = await self._booking.add_booking(user_id, room_id, date_from, date_to)
        return result
