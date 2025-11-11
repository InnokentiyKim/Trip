from src.common.exceptions.common import BaseError
from fastapi import status


class HotelNotFoundException(BaseError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Hotel not found."


class HotelCannotBeUpdatedException(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Hotel cannot be updated."


class HotelAlreadyExistsException(BaseError):
    status_code = status.HTTP_409_CONFLICT
    message = "Hotel already exists."


class HotelProcessingErrorException(BaseError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Hotel processing error."
