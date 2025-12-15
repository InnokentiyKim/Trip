from starlette import status

from src.common.exceptions.common import BaseError


class UserNotFoundException(BaseError):
    """Exception raised when a user is not found."""

    status_code = 404
    message = "User not found."


class UserAlreadyExistsException(BaseError):
    """Exception raised when trying to create a user that already exists."""

    status_code = 409
    message = "User with this email already exists."


class Unauthorized(BaseError):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Unauthorized"
    loc: str = ""


class Forbidden(BaseError):
    status_code: int = status.HTTP_403_FORBIDDEN
    message: str = "Forbidden"
    loc: str = ""
