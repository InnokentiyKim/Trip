from typing import Annotated

from pydantic import EmailStr

from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.controllers.dto.base import BaseRequestDTO


class LoginUserRequestDTO(BaseRequestDTO):
    email: Annotated[str, EmailStr]
    password: str


class AuthUserRequestDTO(LoginUserRequestDTO):
    email: Annotated[str, EmailStr]
    password: str
    user_type: UserRoleEnum
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool = True


class GetUserInfoRequestDTO(BaseRequestDTO):
    email: Annotated[str, EmailStr]
    user_type: UserRoleEnum
    name: str | None = None
    is_active: bool = True
