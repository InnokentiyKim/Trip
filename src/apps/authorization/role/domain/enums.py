from enum import StrEnum


class BaseRoleEnum(StrEnum):
    """Defines the base roles for resources."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class UserRoleEnum(StrEnum):
    """Defines the user roles of those who use resources."""
    ADMIN = BaseRoleEnum.ADMIN
    MANAGER = BaseRoleEnum.MANAGER
    USER = BaseRoleEnum.USER
    GUEST = "guest"
