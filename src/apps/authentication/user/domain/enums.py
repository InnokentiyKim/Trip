from enum import StrEnum


class OAuthProviderEnum(StrEnum):
    YANDEX = "yandex"
    GOOGLE = "google"
    FAKE = "fake"


class UserTypeEnum(StrEnum):
    USER = "user"
    MANAGER = "manager"
