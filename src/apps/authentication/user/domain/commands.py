from src.common.domain.commands import Command


class CreateUserCommand(Command):
    email: str
    password: str
    name: str | None
    phone: str | None
    avatar_url: str | None
    is_active: bool | None


class LoginUserCommand(Command):
    email: str
    password: str


class VerifyUserByTokenCommand(Command):
    token: str
