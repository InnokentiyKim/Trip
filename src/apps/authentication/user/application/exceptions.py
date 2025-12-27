from fastapi import status
from src.common.exceptions.common import BaseError, UniqueConstraintError


class UserNotFoundException(BaseError):
    """Exception raised when a user is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found."


class InvalidCredentialsException(BaseError):
    """Exception raised for invalid login credentials."""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password."


class UserAlreadyExistsException(UniqueConstraintError):
    """Exception raised when trying to create a user that already exists."""
    status_code = status.HTTP_409_CONFLICT
    message = "User with this email already exists."


class Unauthorized(BaseError):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Unauthorized"
    loc: str = ""
