from src.common.exceptions.common import BaseError


class InvalidTokenException(BaseError):
    """Exception raised for invalid tokens."""

    status_code = 401
    detail = "Invalid token."


class InvalidTokenTypeException(BaseError):
    """Exception raised for invalid token type."""

    status_code = 400
    detail = "Invalid token type."


class ExpiredTokenException(BaseError):
    """Exception raised for expired tokens."""

    status_code = 401
    detail = "Token is expired."


class TokenIsMissingException(BaseError):
    """Exception raised when access_token is missing."""

    status_code = 403
    detail = "Token is missing."
