from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.domain.commands import Command


class CreateUserCommand(Command):
    email: str
    password: str
    user_type: UserRoleEnum
    name: str | None
    phone: str | None
    avatar_url: str | None
    is_active: bool | None


class LoginUserCommand(Command):
    email: str
    password: str
