from fastapi import status


class Unauthorized(Exception):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Unauthorized"
    loc: str = ""


class Forbidden(Exception):
    status_code: int = status.HTTP_403_FORBIDDEN
    message: str = "Forbidden"
    loc: str = ""
