from fastapi import status

from src.common.exceptions.common import BaseError


class BookingNotFoundError(BaseError):
    """Exception raised when a booking is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Booking not found."


class BookingCannotBeUpdatedError(BaseError):
    """Exception raised when a booking is not found."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Booking cannot be updated."


class BookingCannotBeConfirmedError(BaseError):
    """Exception raised when a booking can not be confirmed."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Only active pending bookings can be confirmed."


class BookingCannotBeCancelledError(BaseError):
    """Exception raised when a booking is not found."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Booking cannot be updated."


class BookingAlreadyExistsError(BaseError):
    """Exception raised when trying to create a booking that already exists."""

    status_code = status.HTTP_409_CONFLICT
    message = "Booking already exists."


class BookingProcessingError(BaseError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Booking processing error."


class RoomCannotBeBookedError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Room cannot be booked."


class InvalidBookingDatesError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid booking dates."
