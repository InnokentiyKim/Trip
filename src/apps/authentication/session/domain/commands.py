from uuid import UUID

from pydantic import SecretStr

from src.apps.notification.enums import NotificationChannelEnum
from src.common.domain.commands import Command


class CreateAuthSessionCommand(Command):
    user_id: UUID


class ConsumeRefreshTokenCommand(Command):
    refresh_token: SecretStr


class InvalidateRefreshTokenCommand(Command):
    refresh_token: SecretStr


class CreatePasswordResetTokenCommand(Command):
    user_id: UUID


class ConfirmPasswordResetCommand(Command):
    password_reset_token: SecretStr
    password: SecretStr


class CreateOTPCodeCommand(Command):
    user_id: UUID
    recipient: str
    channel: NotificationChannelEnum


class ConsumeOTPCodeCommand(Command):
    user_id: UUID
    plain_code: SecretStr


class CreateMFATokenCommand(Command):
    user_id: UUID


class ValidateMFATokenCommand(Command):
    mfa_token: SecretStr
