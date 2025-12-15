from src.common.exceptions.common import BaseError


class InvalidCredentialsException(BaseError):
    """Exception raised for invalid login credentials."""

    status_code = 401
    detail = "Invalid email or password."


class InvalidTokenException(BaseError):
    """Exception raised for invalid tokens."""

    status_code = 401
    detail = "Invalid token."


class ExpiredTokenException(BaseError):
    """Exception raised for expired tokens."""

    status_code = 401
    detail = "Token is expired."


class TokenIsMissingException(BaseError):
    """Exception raised when a token is missing."""

    status_code = 403
    detail = "Token is missing."
