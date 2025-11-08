from common.exceptions.common import BaseError


class BookingNotFoundException(BaseError):
    """Exception raised when a booking is not found."""
    status_code = 404
    detail = "Booking not found."


class BookingAlreadyExistsException(BaseError):
    """Exception raised when trying to create a booking that already exists."""
    status_code = 409
    detail = "Booking already exists."


class BookingAlreadyDeletedException(BaseError):
    status_code = 409
    detail = "Booking already deleted."


class BookingProcessingErrorException(BaseError):
    status_code = 500
    detail = "Booking processing error."
