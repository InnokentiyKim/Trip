from common.exceptions.common import BaseError


class HotelNotFoundException(BaseError):
    status_code = 404
    message = "Hotel not found."


class HotelAlreadyExistsException(BaseError):
    status_code = 409
    message = "Hotel already exists."


class HotelProcessingErrorException(BaseError):
    status_code = 500
    message = "Hotel processing error."
