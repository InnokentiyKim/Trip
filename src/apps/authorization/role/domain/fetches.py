from dataclasses import dataclass
from uuid import UUID

from src.apps.authorization.role.domain.enums import UserRoleEnum


@dataclass(slots=True, frozen=True)
class GetRoleInfo:
    role_id: UUID
    with_permissions: bool = True


@dataclass(slots=True, frozen=True)
class GetRoleInfoByName:
    role_name: UserRoleEnum
