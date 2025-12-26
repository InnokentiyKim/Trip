from src.common.exceptions.common import BaseError
from fastapi import status


class UnknownResourceTypeError(BaseError):
    """Exception raised when retrieving unknown resource type."""
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Unknown resource type."


class ResourceNotFoundError(BaseError):
    """Exception raised when retrieving unknown resource."""
    status_code = status.HTTP_404_NOT_FOUND
    message = "Resource not found."


class Forbidden(BaseError):
    status_code: int = status.HTTP_403_FORBIDDEN
    message: str = "Forbidden"
    loc: str = ""
