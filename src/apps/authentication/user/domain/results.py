from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import SecretStr

from src.apps.authentication.user.domain.models import User, AuthStatus


@dataclass(slots=True, frozen=True)
class OAuthProviderUser:
    id: str
    name: str
    email: str
    picture: str | None = None


@dataclass(slots=True, frozen=True)
class AuthTokens:
    access_token: SecretStr
    refresh_token: SecretStr


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


@dataclass(slots=True, frozen=True)
class UserInfo:
    id: UUID
    email: str
    role: UUID
    phone: str | None
    name: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime

    auth_info: AuthInfo

    @classmethod
    def from_model(cls, model: User) -> "UserInfo":
        """
        Converts `User` domain entity to the `UserInfo` structure.

        Args:
            model: The `User` entity to convert from.

        Returns:
            UserInfo: A `UserInfo` structure representing the user data.
        """
        auth_info = AuthInfo.from_model(model.auth_status)
        return cls(
            id=model.id,
            email=model.email,
            role=model.role,
            phone=model.phone,
            name=model.name,
            avatar_url=model.avatar_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
            auth_info=auth_info,
        )
