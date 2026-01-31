from enum import StrEnum


class AuthTokenTypeEnum(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    MFA = "mfa"


class PasswordResetTokenStatusEnum(StrEnum):
    CREATED = "created"  # Token created
    VERIFIED = "verified"  # Successfully used
    SUPERSEDED = "superseded"  # A newer token was requested


class OTPStatusEnum(StrEnum):
    CREATED = "created"  # OTP created
    VERIFIED = "verified"  # Successfully used
    SUPERSEDED = "superseded"  # A newer OTP was requested
    FAILED = "failed"  # Invalidated due to too many failed attempts


class OAuthProviderEnum(StrEnum):
    GOOGLE = "google"
    YANDEX = "yandex"
    FACEBOOK = "facebook"
    GITHUB = "github"
