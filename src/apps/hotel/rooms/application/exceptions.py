from src.common.application.exceptions import ExceptionBase


class RoomNotFoundException(ExceptionBase):
    status_code = 404
    detail = "Room not found."


class RoomAlreadyExistsException(ExceptionBase):
    status_code = 409
    detail = "Room already exists."


class RoomProcessingErrorException(ExceptionBase):
    status_code = 500
    detail = "Room processing error."
