from fastapi import status

from src.common.exceptions.common import BaseError


class RoomNotFoundError(BaseError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Room not found."


class RoomCannotBeUpdatedError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "This room can't be updated."


class RoomAlreadyExistsError(BaseError):
    status_code = status.HTTP_409_CONFLICT
    message = "Room already exists."


class RoomProcessingError(BaseError):
    status_code = 500
    message = "Room processing error."
