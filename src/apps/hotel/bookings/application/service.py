from uuid import UUID

from apps.hotel.bookings.application import exceptions
from apps.hotel.bookings.domain import commands
from src.apps.hotel.bookings.domain.model import Booking
from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.common.application.service import ServiceBase


class BookingService(ServiceBase):
    def __init__(
        self,
        booking: BookingAdapter
    ) -> None:
        self._booking = booking

    async def get_booking(self, cmd: commands.GetBookingCommand) -> Booking:
        booking = await self._booking.get_booking_by_id(cmd.booking_id, user_id=cmd.user_id)
        if booking is None:
            raise exceptions.BookingNotFoundException
        return booking

    async def get_bookings_by_status(self, cmd: commands.GetBookingsByStatusCommand) -> list[Booking]:
        bookings = await self._booking.get_bookings(status=cmd.status, user_id=cmd.user_id)
        return bookings

    async def list_bookings(self, cmd: commands.ListBookingsCommand) -> list[Booking]:
        params = cmd.model_dump(exclude={'user_id'}, exclude_unset=True)
        bookings = await self._booking.get_bookings(user_id=cmd.user_id, **params)
        return bookings

    async def delete_booking(self, cmd: commands.DeleteBookingCommand) -> UUID:
        result = await self._booking.delete_booking(cmd.user_id, cmd.booking_id)
        if result is None:
            raise exceptions.BookingNotFoundException
        return result

    async def create_booking(self, cmd: commands.CreateBookingCommand) -> int | None:
        result = await self._booking.add_booking(
            user_id=cmd.user_id, room_id=cmd.room_id, date_from=cmd.date_from, date_to=cmd.date_to
        )
        if result is None:
            raise exceptions.RoomCannotBeBookedException
        return result

    async def update_booking_status(self, cmd: commands.UpdateBookingCommand) -> UUID:
        updated = await self._booking.update_booking(cmd.user_id, cmd.booking_id, status=cmd.status)
        if not updated:
            raise exceptions.BookingNotFoundException
        return updated

    async def cancel_active_booking(self, cmd: commands.CancelActiveBookingCommand) -> UUID:
        booking_id = await self._booking.update_booking(cmd.user_id, cmd.booking_id, only_active=True)
        if booking_id is None:
            raise exceptions.BookingNotFoundException
        return booking_id
