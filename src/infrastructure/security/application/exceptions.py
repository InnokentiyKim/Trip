from src.common.exceptions.common import BaseError


class InvalidCredentialsException(BaseError):
    """Exception raised for invalid login credentials."""

    status_code = 401
    detail = "Invalid email or password."


class InvalidTokenException(BaseError):
    """Exception raised for invalid or expired tokens."""

    status_code = 401
    detail = "Invalid or expired token."


class TokenIsMissingException(BaseError):
    """Exception raised when a token is missing."""

    status_code = 401
    detail = "Token is missing."
