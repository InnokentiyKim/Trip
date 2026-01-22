from typing import Annotated

from pydantic import AnyUrl, EmailStr, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.apps.authentication.user.domain.enums import UserTypeEnum
from src.common.controllers.dto.base import BaseRequestDTO


class AuthRefreshSessionRequestDTO(BaseRequestDTO):
    refresh_token: SecretStr


class LoginUserRequestDTO(BaseRequestDTO):
    email: Annotated[str, EmailStr]
    password: str


class LogoutUserRequestDTO(BaseRequestDTO):
    refresh_token: SecretStr


class RegisterUserRequestDTO(BaseRequestDTO):
    email: EmailStr
    password: str
    user_type: UserTypeEnum
    name: str | None = None
    phone: PhoneNumber | None = None
    avatar_url: AnyUrl | None = None
    is_active: bool = True
