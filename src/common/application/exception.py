from fastapi import HTTPException


class GeneralError(Exception):
    """Base class for application-specific errors."""

    status_code: int = 500
    message: str = "An internal server error occurred"
    loc: str = "general"

    def __init__(self, message: str = "", loc: str = "", status_code: int = 0):
        # Use provided arguments, otherwise fall back to class defaults
        self.message = message or self.message
        self.loc = loc or self.loc
        self.status_code = status_code or self.status_code

        super().__init__(self.message)


class ExceptionBase(HTTPException):
    """Base class for all custom exceptions in the application."""
    status_code: int = 500
    detail: str = "An internal server error occurred"
    loc: str = ""
