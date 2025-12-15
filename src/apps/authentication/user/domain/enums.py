from enum import StrEnum


class AuthTokenTypeEnum(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    MFA = "mfa"


class OAuthProviderEnum(StrEnum):
    YANDEX = "yandex"
    GOOGLE = "google"
    FAKE = "fake"
