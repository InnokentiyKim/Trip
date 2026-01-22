from dataclasses import dataclass
from uuid import UUID

from src.apps.authorization.access.domain.enums import PermissionEnum, ResourceTypeEnum
from src.apps.authorization.role.domain.enums import UserRoleEnum


@dataclass(slots=True, frozen=True)
class UserAccessInfo:
    user_id: UUID
    role: PermissionEnum | UserRoleEnum
    resource_id: UUID
    resource_type: ResourceTypeEnum

    @property
    def user_type(self) -> ResourceTypeEnum:
        """Get the user resource type."""
        return ResourceTypeEnum.USER
