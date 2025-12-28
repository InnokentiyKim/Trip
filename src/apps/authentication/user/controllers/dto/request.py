from typing import Annotated

from pydantic import EmailStr, SecretStr

from src.apps.authentication.user.domain.enums import UserTypeEnum
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.controllers.dto.base import BaseRequestDTO


class LoginUserRequestDTO(BaseRequestDTO):
    email: Annotated[str, EmailStr]
    password: str


class LogoutUserRequestDTO(BaseRequestDTO):
    refresh_token: SecretStr


class AuthUserRequestDTO(LoginUserRequestDTO):
    email: Annotated[str, EmailStr]
    password: SecretStr
    user_type: UserTypeEnum
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool = True


class GetUserInfoRequestDTO(BaseRequestDTO):
    email: Annotated[str, EmailStr]
    user_type: UserRoleEnum
    name: str | None = None
    is_active: bool = True
