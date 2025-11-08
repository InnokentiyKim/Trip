from common.exceptions.common import BaseError


class RoomNotFoundException(BaseError):
    status_code = 404
    detail = "Room not found."


class RoomAlreadyExistsException(BaseError):
    status_code = 409
    detail = "Room already exists."


class RoomProcessingErrorException(BaseError):
    status_code = 500
    detail = "Room processing error."
