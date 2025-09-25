from src.common.application.exceptions import ExceptionBase


class BookingNotFoundException(ExceptionBase):
    """Exception raised when a booking is not found."""
    status_code = 404
    detail = "Booking not found."


class BookingAlreadyExistsException(ExceptionBase):
    """Exception raised when trying to create a booking that already exists."""
    status_code = 409
    detail = "Booking already exists."


class BookingAlreadyDeletedException(ExceptionBase):
    status_code = 409
    detail = "Booking already deleted."


class BookingProcessingErrorException(ExceptionBase):
    status_code = 500
    detail = "Booking processing error."
