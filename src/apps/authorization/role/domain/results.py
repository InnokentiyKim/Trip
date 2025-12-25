from dataclasses import dataclass
from uuid import UUID

from src.apps.authorization.access.domain.enums import ResourceTypeEnum
from src.apps.authorization.access.domain.models import Permission, Role


@dataclass(slots=True, frozen=True)
class PermissionInfo:
    id: UUID
    resource_type: ResourceTypeEnum
    name: str
    description: str

    @classmethod
    def from_model(cls, model: Permission) -> "PermissionInfo":
        """Create a PermissionInfo instance from a Permission domain model."""
        return cls(id=model.id, resource_type=model.resource_type, name=model.name, description=model.description)


@dataclass(slots=True, frozen=True)
class RoleInfo:
    id: UUID
    name: str
    description: str | None
    permissions: list[PermissionInfo]

    @classmethod
    def from_model(cls, model: Role) -> "RoleInfo":
        """
        Create a RoleFullInfo instance from a Role domain model and an optional list of permissions.

        Args:
            model (Role): The Role domain model instance.

        Returns:
            RoleInfo: The corresponding RoleFullInfo dataclass.
        """
        permissions_list = [PermissionInfo.from_model(perm) for perm in model.permissions]
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            permissions=permissions_list,
        )
