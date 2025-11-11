from fastapi import status

from src.common.exceptions.common import BaseError


class Unauthorized(BaseError):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Unauthorized"
    loc: str = ""


class Forbidden(BaseError):
    status_code: int = status.HTTP_403_FORBIDDEN
    message: str = "Forbidden"
    loc: str = ""
