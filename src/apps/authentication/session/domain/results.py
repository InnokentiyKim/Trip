from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import SecretStr

from src.apps.authentication.session.domain.enums import PasswordResetTokenStatusEnum, OTPStatusEnum
from src.apps.authentication.user.domain.models import AuthStatus
from src.apps.notification.enums import NotificationChannelEnum


@dataclass(slots=True, frozen=True)
class OAuthProviderUser:
    id: str
    name: str
    email: str
    picture: str | None = None


@dataclass(slots=True, frozen=True)
class UserID:
    id: UUID


@dataclass(slots=True, frozen=True)
class AuthTokens:
    access_token: SecretStr
    refresh_token: SecretStr


@dataclass(slots=True, frozen=True)
class PasswordResetTokenInfo:
    id: UUID
    user_id: UUID
    reset_token: SecretStr
    hashed_reset_token: str
    created_at: datetime
    expires_at: datetime
    status: PasswordResetTokenStatusEnum


@dataclass(slots=True, frozen=True)
class OTPCodeInfo:
    id: UUID
    user_id: UUID
    channel: NotificationChannelEnum
    otp_code: str
    hashed_otp_code: str
    failed_attempts: int
    created_at: datetime
    expires_at: datetime
    status: OTPStatusEnum


@dataclass(slots=True, frozen=True)
class MFAToken:
    mfa_token: SecretStr


@dataclass(slots=True, frozen=True)
class AuthInfo:
    mfa_email_enabled: bool = False
    mfa_sms_enabled: bool = False

    @classmethod
    def from_model(cls, model: AuthStatus) -> "AuthInfo":
        """
        Converts `User` domain entity to the `AuthInfo` structure.

        Args:
            model: The `User` entity to convert from.

        Returns:
            AuthInfo: A `AuthInfo` structure representing the authentication data.
        """
        return cls(
            mfa_email_enabled=model.mfa_email_enabled,
            mfa_sms_enabled=model.mfa_sms_enabled,
        )

    @property
    def is_mfa_enabled(self) -> bool:
        """Returns True if any MFA method is enabled."""
        return self.mfa_email_enabled or self.mfa_sms_enabled