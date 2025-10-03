from enum import StrEnum


class UserRoleEnum(StrEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    MODERATOR = "moderator"
    MANAGER = "manager"
