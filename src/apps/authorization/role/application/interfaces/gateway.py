from abc import abstractmethod
from uuid import UUID

from src.apps.authorization.access.domain.models import Permission, Role
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.interfaces import GatewayProto


class RoleGatewayProto(GatewayProto):
    @abstractmethod
    async def add(self, role: Role) -> None:
        """
        Adds a new role_id to the database.

        Args:
            role (Role): The role_id entity to be added.

        Returns:
            None
        """
        ...

    @abstractmethod
    async def get(self, role_id: UUID) -> Role | None:
        """
        Retrieves a role_id from the database by its unique role_code.

        Args:
            role_id (str): The unique code of the role_id.

        Returns:
            Role | None: The Role object if found, otherwise None.
        """
        ...

    @abstractmethod
    async def get_by_name(self, role_name: UserRoleEnum) -> Role | None:
        """
        Retrieves a role_id from the database by its unique name.

        Args:
            role_name (str): The unique name of the role_id.

        Returns:
            Role | None: The Role object if found, otherwise None.
        """
        ...

    @abstractmethod
    async def get_all_users_granted_to_role(self, role_id: UUID) -> list[UUID]:
        """
        Retrieves all user IDs granted to the specified role_id.

        Args:
            role_id (UUID): The unique identifier of the role_id.

        Returns:
            list[UUID]: A list of user IDs granted to the role_id.
        """
        ...

    @abstractmethod
    async def delete(self, role_id: UUID) -> bool:
        """
        Deletes a role_id from the database by its unique identifier.

        Args:
            role_id (UUID): The unique identifier of the role_id to delete.

        Returns:
            bool: True if the role_id was deleted, False if the role_id was not found.
        """
        ...


class PermissionGatewayProto(GatewayProto):
    @abstractmethod
    async def add(self, permission: Permission) -> None:
        """Adds a new permission to the database."""
        ...

    @abstractmethod
    async def list_all_permissions(self) -> list[Permission]:
        """
        Returns a list of permission names associated with the specified role_id.

        Returns:
            RolePermissionsListReturn: A list of permission names linked to the role_id.
        """
        ...

    @abstractmethod
    async def get_list(self, permission_ids: list[UUID]) -> list[Permission]:
        """
        Returns a list of permission IDs from the input list that are not found in the database.

        Args:
            permission_ids (list[UUID]): List of permission UUIDs to check.

        Returns:
            list[Permission]: List of Permissions
        """
        ...
