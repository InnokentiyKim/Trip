from common.application.exceptions import ExceptionBase


class HotelNotFoundException(ExceptionBase):
    status_code = 404
    detail = "Hotel not found."


class HotelAlreadyExistsException(ExceptionBase):
    status_code = 409
    detail = "Hotel already exists."


class HotelProcessingErrorException(ExceptionBase):
    status_code = 500
    detail = "Hotel processing error."
