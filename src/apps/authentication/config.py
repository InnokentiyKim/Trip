from enum import StrEnum

from pydantic import BaseModel, SecretStr, Field
from pydantic_settings import BaseSettings

from src.apps.authentication.session.domain.models import OTPCode, PasswordResetToken, AuthSession
from src.apps.authentication.user.domain.models import User
from src.common.domain.enums import DataAccessEnum


class AuthGatewayEnum(StrEnum):
    ALCHEMY = DataAccessEnum.ALCHEMY
    MEMORY = DataAccessEnum.MEMORY


class UserConfig(BaseSettings):
    gateway: AuthGatewayEnum = AuthGatewayEnum.ALCHEMY
    fake_data: list[User] = []


class CoreAuthSettings(BaseSettings):
    max_current_sessions_per_user: int = 5

    access_token_lifetime_minutes: int = 50
    refresh_token_lifetime_minutes: int = 10080

    reset_password_token_lifetime_minutes: int = 30
    reset_password_path: str = "auth/password/new/"

    otp_max_attempts: int = 3
    otp_lifetime_minutes: int = 5
    mfa_token_lifetime_minutes: int = 10


class AuthSessionConfig(BaseModel):
    gateway: AuthGatewayEnum = AuthGatewayEnum.ALCHEMY
    fake_data: list[AuthSession] = []


class PasswordResetTokenConfig(BaseModel):
    gateway: AuthGatewayEnum = AuthGatewayEnum.ALCHEMY
    fake_data: list[PasswordResetToken] = []


class OTPCodeConfig(BaseModel):
    gateway: AuthGatewayEnum = AuthGatewayEnum.ALCHEMY
    fake_data: list[OTPCode] = []


class AdminSettings(BaseSettings):
    admin_email: str = "admin@mail.com"
    admin_password: SecretStr = SecretStr("Password123")


class AuthConfig(BaseSettings):
    user: UserConfig = UserConfig()
    core: CoreAuthSettings = Field(default_factory=CoreAuthSettings)
    admin: AdminSettings = Field(default_factory=AdminSettings)
    auth_session: AuthSessionConfig = Field(default_factory=AuthSessionConfig)
    password_reset_token: PasswordResetTokenConfig = Field(default_factory=PasswordResetTokenConfig)
    otp: OTPCodeConfig = Field(default_factory=OTPCodeConfig)
