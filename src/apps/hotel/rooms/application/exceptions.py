from common.exceptions.common import BaseError


class RoomNotFoundException(BaseError):
    status_code = 404
    message = "Room not found."


class RoomAlreadyExistsException(BaseError):
    status_code = 409
    message = "Room already exists."


class RoomProcessingErrorException(BaseError):
    status_code = 500
    message = "Room processing error."
