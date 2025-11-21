from datetime import date
from uuid import UUID

from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.common.domain.commands import Command


class GetBookingCommand(Command):
    user_id: UUID
    booking_id: UUID


class GetActiveBookingsCommand(Command):
    user_id: UUID


class GetBookingsByStatusCommand(Command):
    user_id: UUID
    status: BookingStatusEnum


class ListBookingsCommand(Command):
    user_id: UUID
    room_id: int | None
    date_from: date | None
    status: BookingStatusEnum | None


class DeleteBookingCommand(Command):
    user_id: UUID
    booking_id: UUID


class CreateBookingCommand(Command):
    user_id: UUID
    room_id: int
    date_from: date
    date_to: date


class UpdateBookingCommand(Command):
    user_id: int
    booking_id: UUID
    status: BookingStatusEnum


class CancelActiveBookingCommand(Command):
    user_id: UUID
    booking_id: UUID
