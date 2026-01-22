from fastapi import status
from sqlalchemy.exc import IntegrityError


class BaseError(Exception):
    """Base class for application-specific errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "An internal server error occurred"
    loc: str = "general"

    def __init__(self, message: str = "", loc: str = "", status_code: int = 0):
        # Use provided arguments, otherwise fall back to class defaults
        self.message = message or self.message
        self.loc = loc or self.loc
        self.status_code = status_code or self.status_code

        super().__init__(self.message)


class UniqueConstraintError(BaseError, IntegrityError):
    status_code: int = status.HTTP_409_CONFLICT
    message: str = "Item already exists"

    def __init__(
        self,
        message: str = "",
        loc: str = "",
        status_code: int = 0,
    ) -> None:
        self.message = message or self.message
        self.loc = loc or self.loc
        self.status_code = status_code or self.status_code

        Exception.__init__(self, self.message)


class InternalError(BaseError):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Internal error"
    loc: str = "general"
