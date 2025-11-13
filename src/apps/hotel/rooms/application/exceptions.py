from src.common.exceptions.common import BaseError
from fastapi import status


class RoomNotFoundException(BaseError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Room not found."


class RoomCannotBeUpdatedException(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Room can't be updated."


class RoomAlreadyExistsException(BaseError):
    status_code = status.HTTP_409_CONFLICT
    message = "Room already exists."


class RoomProcessingErrorException(BaseError):
    status_code = 500
    message = "Room processing error."
