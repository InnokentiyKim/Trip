from common.exceptions.common import BaseError


class HotelNotFoundException(BaseError):
    status_code = 404
    detail = "Hotel not found."


class HotelAlreadyExistsException(BaseError):
    status_code = 409
    detail = "Hotel already exists."


class HotelProcessingErrorException(BaseError):
    status_code = 500
    detail = "Hotel processing error."
