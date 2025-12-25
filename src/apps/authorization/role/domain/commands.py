from uuid import UUID

from src.apps.authorization.access.domain.enums import ResourceTypeEnum
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.domain.commands import Command


class CreateCustomRole(Command):
    code: str
    name: UserRoleEnum
    permissions: list[UUID]
    resource_type: ResourceTypeEnum
    description: str | None


class RemovePermissionsFromRole(Command):
    role_id: UUID
    permissions: list[UUID]


class DeleteRole(Command):
    role_id: UUID


class AssignPermissionsToRole(Command):
    role_id: UUID
    permissions: list[UUID]
