from typing import Annotated

from pydantic import EmailStr


class LoginUserRequestDTO:
    email: Annotated[str, EmailStr]
    password: str


class AuthUserRequestDTO(LoginUserRequestDTO):
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool = True
