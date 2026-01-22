from uuid import UUID

from src.apps.authorization.access.domain.enums import PermissionEnum, ResourceTypeEnum
from src.common.domain.commands import Command


class VerifyUserByTokenCommand(Command):
    access_token: str


class Authorize(Command):
    access_token: str
    permission: PermissionEnum
    resource_type: ResourceTypeEnum
    resource_id: UUID | int | None = None

    def __repr__(self) -> str:
        """Represent the command as a string."""
        return (
            f"Authorize(permission={self.permission},"
            f" resource_type={self.resource_type},"
            f" resource_id={self.resource_id})"
        )
