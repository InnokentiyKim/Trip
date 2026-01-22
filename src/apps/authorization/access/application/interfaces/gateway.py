from abc import abstractmethod
from uuid import UUID

from src.apps.authorization.access.domain.enums import PermissionEnum, ResourceTypeEnum
from src.common.interfaces import GatewayProto


class AccessGatewayProto(GatewayProto):
    @abstractmethod
    async def is_resource_owner(self, user_id: UUID, object_type: ResourceTypeEnum, object_id: UUID | int) -> bool:
        """
        Check if the user is the owner of the resource.

        Args:
            user_id (UUID): The unique identifier of the user.
            object_type (ResourceTypeEnum): The type of the object.
            object_id (UUID | int): The unique identifier of the object.

        Returns:
            bool: True if the user is the owner of the resource, False otherwise.
        """
        ...

    @abstractmethod
    async def check_object_access(
        self,
        user_id: UUID,
        user_role: UUID,
        object_type: ResourceTypeEnum,
        object_id: UUID | int,
    ) -> bool:
        """
        Check if a user has access to a specific object.

        Args:
            user_id (UUID): The unique identifier of the user.
            user_role (UUID): The unique identifier of the user's role_id.
            object_type (ResourceTypeEnum): The type of the object.
            object_id (UUID | int): The unique identifier of the object.

        Returns:
            bool: True if the user has access, False otherwise.
        """
        ...

    @abstractmethod
    async def check_permission(
        self, role_id: UUID, resource_type: ResourceTypeEnum, permission: PermissionEnum
    ) -> bool:
        """
        Check if a subject has a specific permission.

        Args:
            role_id (UUID): The unique identifier of the role_id.
            resource_type (ResourceTypeEnum): The type of the resource.
            permission (PermissionEnum): The permission to check.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        ...
