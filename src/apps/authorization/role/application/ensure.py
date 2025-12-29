from uuid import UUID

from src.apps.authorization.access.domain.models import Role, Permission
from src.apps.authorization.role.application.interfaces.gateway import RoleGatewayProto, PermissionGatewayProto
from src.apps.authorization.role.domain.enums import BaseRoleEnum, UserRoleEnum
from src.common.interfaces import CustomLoggerProto
from src.apps.authorization.role.application import exceptions


class RoleServiceEnsurance:
    def __init__(self, roles: RoleGatewayProto, logger: CustomLoggerProto) -> None:
        self._roles = roles
        self._logger = logger

    async def role_exists(self, role_id: UUID) -> Role:
        """
        Ensure that a role with the given ID exists.

        Args:
            role_id (UUID): The ID of the role to check.

        Returns:
            Role: The role object.

        Raises:
            RoleIsNotFoundError: If the role does not exist.
        """
        role = await self._roles.get(role_id)

        if not role:
            self._logger.error("Role is not found", role_id=role_id)
            raise exceptions.RoleIsNotFoundError from None

        return role

    async def role_name_is_not_base(self, role_name: UserRoleEnum) -> None:
        """
        Ensure that the role code is not a base role.

        Args:
            role_name (UserRoleEnum): The name of the role to check.

        Raises:
            RoleCouldNotBeDeletedError: If the role code is a base role.
        """
        # Prohibit to delete base roles
        if role_name in BaseRoleEnum:
            self._logger.error("Base role could not be removed")
            raise exceptions.RoleCouldNotBeDeletedError from None

    async def no_users_granted_to_role(self, role_id: UUID) -> None:
        """
        Ensure that no users are granted to the specified role.

        Args:
            role_id (UUID): The role's ID to check.

        Raises:
            RoleCouldNotBeDeletedError: If there are users granted to the role.
        """
        if await self._roles.get_all_users_granted_to_role(role_id):
            self._logger.error("Role could not be deleted because there are users granted to it", role_id=role_id)
            raise exceptions.RoleCouldNotBeDeletedError from None

    @staticmethod
    async def ensure_permissions_exist(
        permissions_ids: list[UUID], permissions: PermissionGatewayProto, logger: CustomLoggerProto
    ) -> list[Permission]:
        """
        Ensures that all specified permission IDs exist in the system.

        Args:
            permissions_ids (list[UUID]): List of permission UUIDs to check.
            permissions (PermissionsGatewayProto): Gateway to access permissions.
            logger (CustomLoggerProto): Logger for error reporting.

        Returns:
            list[Permission]: List of found Permission objects.

        Raises:
            PermissionsNotFoundError: If any of the specified permissions do not exist.
        """
        permission_objects = await permissions.get_list(permissions_ids)
        found_permissions = [permission.id for permission in permission_objects]

        if len(found_permissions) < len(permissions_ids):
            not_found_permissions = set(permissions_ids) - set(found_permissions)
            error_message = f"Some of permissions do not exist {not_found_permissions}"
            logger.error(error_message)
            raise exceptions.PermissionsNotFoundError(message=error_message)

        return permission_objects
