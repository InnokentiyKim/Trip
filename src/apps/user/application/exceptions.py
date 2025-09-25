from src.common.application.exceptions import ExceptionBase


class UserNotFoundException(ExceptionBase):
    """Exception raised when a user is not found."""
    status_code = 404
    detail = "User not found."


class UserAlreadyExistsException(ExceptionBase):
    """Exception raised when trying to create a user that already exists."""
    status_code = 409
    detail = "User with this email already exists."
