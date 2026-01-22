from fastapi import status

from src.common.exceptions.common import BaseError


class HotelNotFoundError(BaseError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Hotel not found."


class HotelCannotBeUpdatedError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Hotel updating failed."


class HotelAlreadyExistsError(BaseError):
    status_code = status.HTTP_409_CONFLICT
    message = "Hotel already exists."


class HotelProcessingError(BaseError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Hotel processing error."
