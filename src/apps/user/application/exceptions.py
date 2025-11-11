from src.common.exceptions.common import BaseError


class UserNotFoundException(BaseError):
    """Exception raised when a user is not found."""
    status_code = 404
    message = "User not found."


class UserAlreadyExistsException(BaseError):
    """Exception raised when trying to create a user that already exists."""
    status_code = 409
    message = "User with this email already exists."
