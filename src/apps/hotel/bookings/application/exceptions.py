from src.common.exceptions.common import BaseError
from fastapi import status


class BookingNotFoundException(BaseError):
    """Exception raised when a booking is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Booking not found."


class BookingCannotBeUpdatedException(BaseError):
    """Exception raised when a booking is not found."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Booking cannot be updated."


class BookingCannotBeConfirmedException(BaseError):
    """Exception raised when a booking can not be confirmed."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Only active pending bookings can be confirmed."


class BookingCannotBeCancelledException(BaseError):
    """Exception raised when a booking is not found."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Booking cannot be updated."


class BookingAlreadyExistsException(BaseError):
    """Exception raised when trying to create a booking that already exists."""

    status_code = status.HTTP_409_CONFLICT
    message = "Booking already exists."


class BookingProcessingErrorException(BaseError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Booking processing error."


class RoomCannotBeBookedException(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Room cannot be booked."


class InvalidBookingDatesException(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid booking dates."
