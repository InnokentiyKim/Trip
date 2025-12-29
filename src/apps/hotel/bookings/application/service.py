from uuid import UUID

from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.apps.hotel.bookings.application import exceptions
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.bookings.domain import commands
from src.apps.hotel.bookings.domain.models import Booking
from src.common.application.service import ServiceBase
from src.apps.hotel.bookings.application.ensure import BookingServiceInsurance
from src.common.interfaces import CustomLoggerProto


class BookingService(ServiceBase):
    def __init__(self, gateway: BookingGatewayProto, logger: CustomLoggerProto) -> None:
        self._adapter = gateway
        self._logger = logger
        self._ensure = BookingServiceInsurance(gateway, logger)

    async def get_booking(self, cmd: commands.GetBookingCommand) -> Booking:
        booking = await self._ensure.booking_exists(cmd.booking_id, cmd.user_id)
        return booking

    async def get_active_bookings(
        self, cmd: commands.GetActiveBookingsCommand
    ) -> list[Booking]:
        bookings = await self._adapter.get_active_bookings(user_id=cmd.user_id)
        return bookings

    async def get_bookings_by_status(
        self, cmd: commands.GetBookingsByStatusCommand
    ) -> list[Booking]:
        bookings = await self._adapter.get_bookings(
            status=cmd.status, user_id=cmd.user_id
        )
        return bookings

    async def list_bookings(self, cmd: commands.ListBookingsCommand) -> list[Booking]:
        params = cmd.model_dump(exclude={"user_id"}, exclude_unset=True)
        bookings = await self._adapter.get_bookings(user_id=cmd.user_id, **params)
        return bookings

    async def delete_booking(self, cmd: commands.DeleteBookingCommand) -> None:
        booking = await self._ensure.booking_exists(cmd.booking_id, cmd.user_id)

        if booking.status == BookingStatusEnum.CANCELLED or BookingStatusEnum.COMPLETED:
            await self._adapter.delete_booking(booking)
            self._logger.info("Booking successfully deleted", booking_id=str(cmd.booking_id))

    async def create_booking(self, cmd: commands.CreateBookingCommand) -> Booking | None:
        if cmd.date_from > cmd.date_to:
            self._logger.error("Date from/to must be before date", booking_id=cmd.booking_id)
            raise exceptions.InvalidBookingDatesException

        booking = await self._adapter.add_booking(
            user_id=cmd.user_id,
            room_id=cmd.room_id,
            date_from=cmd.date_from,
            date_to=cmd.date_to,
        )

        if booking is None:
            self._logger.error(
                "Room cannot be booked for the selected dates",
                room_id=cmd.room_id, date_from=str(cmd.date_from), date_to=str(cmd.date_to)
            )
            raise exceptions.RoomCannotBeBookedException

        self._logger.info("New booking successfully created", booking_id=booking.id)
        return booking

    async def confirm_booking(self, cmd: commands) -> UUID:
        booking = await self._ensure.booking_exists(cmd.booking_id, cmd.user_id)
        if not booking.status.PENDING:
            self._logger.error("Booking confirmation failed", booking_id=cmd.booking_id)
            raise exceptions.BookingCannotBeConfirmedException

        booking_id = await self._adapter.update_booking(booking, only_active=True, status=BookingStatusEnum.CONFIRMED)
        if not booking_id:
            self._logger.error("Booking confirmation failed", booking_id=cmd.booking_id)
            raise exceptions.BookingCannotBeConfirmedException

        return booking_id

    async def update_booking_status(self, cmd: commands.UpdateBookingCommand) -> None:
        booking = await self._ensure.booking_exists(cmd.booking_id, cmd.user_id)
        is_updated = await self._adapter.update_booking(booking, status=cmd.status)
        if not is_updated:
            self._logger.error("Booking update failed", booking_id=cmd.booking_id)
            raise exceptions.BookingCannotBeUpdatedException

        self._logger.info("Booking status updated", booking_id=booking.id, new_status=cmd.status.value)

    async def cancel_active_booking(
        self, cmd: commands.CancelActiveBookingCommand
    ) -> UUID:
        booking = await self._ensure.booking_exists(cmd.booking_id, cmd.user_id)

        if booking.status != BookingStatusEnum.PENDING:
            self._logger.error("Booking cancellation failed", user_id=cmd.user_id, booking_id=cmd.booking_id)
            raise exceptions.BookingCannotBeCancelledException

        cancelled_id = await self._adapter.update_booking(
            booking, only_active=True, status=BookingStatusEnum.CANCELLED
        )

        if cancelled_id is None:
            self._logger.error("Booking cancellation failed", user_id=cmd.user_id, booking_id=cmd.booking_id)
            raise exceptions.BookingCannotBeCancelledException

        self._logger.info("Booking successfully cancelled", user_id=cmd.user_id, booking_id=cmd.booking_id)
        return cancelled_id
