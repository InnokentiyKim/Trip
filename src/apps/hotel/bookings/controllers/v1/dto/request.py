from datetime import date
from uuid import UUID

from pydantic import field_validator

from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.common.controllers.dto.base import BaseDTO


class ListBookingsRequestDTO(BaseDTO):
    room_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    status: BookingStatusEnum | None = None

    @field_validator("date_to")
    @classmethod
    def validate_dates(cls, v: date | None, info) -> date | None:
        """Validate that date_to is after date_from."""
        if v and info.data.get("date_from") and v <= info.data["date_from"]:
            raise ValueError("date_to must be after date_from")
        return v


class CreateBookingRequestDTO(BaseDTO):
    room_id: UUID
    date_from: date
    date_to: date

    @field_validator("date_to")
    @classmethod
    def validate_dates(cls, date_to: date, info) -> date:
        """Validate that date_to is after date_from."""
        if "date_from" in info.data:
            date_from = info.data["date_from"]
            if date_to < date_from:
                raise ValueError("date_to must be after date_from")
        return date_to
