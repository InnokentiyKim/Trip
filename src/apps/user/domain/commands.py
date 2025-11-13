from src.common.domain.commands import Command


class CreateUserCommand(Command):
    email: str
    password: str
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool = True


class LoginUserCommand(Command):
    email: str
    password: str


class VerifyUserByTokenCommand(Command):
    token: str
