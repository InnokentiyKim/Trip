from src.common.application.exceptions import ExceptionBase


class InvalidCredentialsException(ExceptionBase):
    """Exception raised for invalid login credentials."""
    status_code = 401
    detail = "Invalid email or password."


class InvalidTokenException(ExceptionBase):
    """Exception raised for invalid or expired tokens."""
    status_code = 401
    detail = "Invalid or expired token."


class TokenIsMissingException(ExceptionBase):
    """Exception raised when a token is missing."""
    status_code = 401
    detail = "Token is missing."
