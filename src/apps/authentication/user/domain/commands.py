from pydantic import SecretStr

from src.apps.authentication.user.domain.enums import UserTypeEnum
from src.common.domain.commands import Command


class CreateUserCommand(Command):
    email: str
    password: SecretStr
    user_type: UserTypeEnum
    name: str | None
    phone: str | None
    avatar_url: str | None
    is_active: bool | None


class VerifyUserCredentialsCommand(Command):
    email: str
    password: SecretStr
