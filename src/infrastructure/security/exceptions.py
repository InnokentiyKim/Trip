from fastapi import status

from src.common.exceptions.common import BaseError


class InvalidTokenError(BaseError):
    """Exception raised for invalid tokens."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token."


class InvalidTokenTypeError(BaseError):
    """Exception raised for invalid token type."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token type."


class ExpiredTokenError(BaseError):
    """Exception raised for expired tokens."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token is expired."


class TokenIsMissingError(BaseError):
    """Exception raised when access_token is missing."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token is missing."
