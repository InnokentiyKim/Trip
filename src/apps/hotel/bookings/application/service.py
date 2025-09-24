from typing import Any

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
        return booking

    async def get_bookings(self, **filters) -> list[Bookings]:
        bookings = await self._booking.get_bookings(**filters)
        return bookings

    async def delete_booking(self, booking_id: int) -> None:
        await self._booking.delete_booking(booking_id)

    async def add_booking(self, booking: Bookings) -> None:
        await self._booking.add_booking(booking)
