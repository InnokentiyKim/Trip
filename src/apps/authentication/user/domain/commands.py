from typing import Annotated

from pydantic import AnyUrl, SecretStr

from src.apps.authentication.user.domain.enums import UserTypeEnum
from src.common.domain.commands import Command


class CreateUserCommand(Command):
    email: str
    password: SecretStr
    user_type: UserTypeEnum
    name: str | None
    phone: str | None
    avatar_url: Annotated[str, AnyUrl] | None
    is_active: bool = True


class VerifyUserCredentialsCommand(Command):
    email: str
    password: SecretStr
