import uuid

from src.apps.authorization.access.domain.models import Role
from src.apps.authorization.role.application.ensure import RoleServiceEnsurance
from src.apps.authorization.role.application.exceptions import RoleIsNotFoundError
from src.apps.authorization.role.application.interfaces.gateway import RoleGatewayProto, PermissionGatewayProto
from src.common.interfaces import CustomLoggerProto
from src.apps.authorization.role.domain import commands
from src.apps.authorization.role.domain import results
from src.apps.authorization.role.domain import fetches


class RoleManagementService:  # noqa: WPS214
    def __init__(
        self,
        gateway: RoleGatewayProto,
        permissions: PermissionGatewayProto,
        logger: CustomLoggerProto,
    ) -> None:
        self._gateway = gateway
        self._permissions = permissions
        self._logger = logger
        self._ensure = RoleServiceEnsurance(gateway, logger)

    async def create_role(
        self, cmd: commands.CreateCustomRole
    ) -> results.RoleInfo:
        """
        Creates a new custom role with the specified permissions.

        Args:
            cmd (CreateCustomRole): Command containing role details and permissions.

        Returns:
            RoleFullInfo: Information about the created role.

        Raises:
            PermissionsNotFoundError: If any of the specified permissions do not exist.
            RoleAlreadyExistsError: If a role with the same code already exists.
        """
        permissions = await self._permissions.get_list(cmd.permissions)

        # Create role
        role = Role(
            id=uuid.uuid4(),
            name=cmd.name,
            description=cmd.description,
        )
        await role.add_permissions(permissions)
        await self._gateway.add(role)

        self._logger.debug("Role created", role_id=role.id, role_name=cmd.name)
        return results.RoleInfo.from_model(role)

    async def delete_role(
        self, cmd: commands.DeleteRole
    ) -> results.RoleInfo:
        """
        Deletes a role by its ID.

        Args:
            cmd (src.apps.authorization.role.domain.commands.DeleteRole): Command containing the role ID to delete.

        Raises:
            RoleIsNotFoundError: If the role does not exist.
            RoleCouldNotBeDeletedError: If the role is a base role and cannot be deleted.
            RoleAssignedToUsersError: If the role is assigned to users and cannot be deleted.
        """
        # Ensure role exists and can be deleted
        role = await self._ensure.role_exists(cmd.role_id)
        await self._ensure.role_name_is_not_base(role.name)
        await self._ensure.no_users_granted_to_role(role.id)

        await self._gateway.delete(role.id)

        self._logger.debug("Role deleted", role_id=role.id, role_name=role.name)
        return results.RoleInfo.from_model(role)

    async def get_role_info(self, fetch: fetches.GetRoleInfo) -> results.RoleInfo:
        """
        Retrieves detailed information about a role, including its permissions.

        Args:
            fetch (GetRoleInfo): Object containing the role ID to fetch.

        Returns:
            RoleFullInfo: Information about the role and its permissions.

        Raises:
            RoleIsNotFoundError: If the role does not exist.
        """
        role = await self._ensure.role_exists(fetch.role_id)

        self._logger.debug("Role info retrieved", role_id=role.id, role_name=role.name)
        return results.RoleInfo.from_model(role)

    async def get_role_info_by_name(self, fetch: fetches.GetRoleInfoByName) -> results.RoleInfo:
        """
        Retrieves detailed information about a role, including its permissions.

        Args:
            fetch (GetRoleInfoByName): Object containing the role ID to fetch.

        Returns:
            RoleFullInfo: Information about the role and its permissions.

        Raises:
            RoleIsNotFoundError: If the role does not exist.
        """
        role = await self._gateway.get_by_name(fetch.role_name)

        if role is None:
            self._logger.error("Role is not found", role_name=fetch.role_name)
            raise RoleIsNotFoundError from None

        self._logger.debug("Role info retrieved", role_id=role.id, role_name=role.name)
        return results.RoleInfo.from_model(role)

    async def assign_permissions_to_role(
        self, cmd: commands.AssignPermissionsToRole
    ) -> results.RoleInfo:
        """
        Assigns a list of permissions to a specific role.

        Args:
            cmd (AssignPermissionsToRole): Command containing the role ID and permissions to assign.

        Returns:
            RoleFullInfo: Information about the role with its updated permissions.

        Raises:
            RoleIsNotFoundError: If the role does not exist.
            PermissionsNotFoundError: If any of the specified permissions do not exist.
        """
        role = await self._ensure.role_exists(cmd.role_id)
        permissions = await self._permissions.get_list(cmd.permissions)

        await role.add_permissions(permissions)
        await self._gateway.add(role)

        self._logger.debug("Permissions assigned to role", role_id=role.id, role_name=role.name)
        return results.RoleInfo.from_model(role)

    async def remove_permissions_from_role(
        self, cmd: commands.RemovePermissionsFromRole
    ) -> results.RoleInfo:
        """
        Removes specified permissions from a role.

        Args:
            cmd (RemovePermissionsFromRole): Command containing the role ID and permissions to remove.

        Raises:
            RoleIsNotFoundError: If the role does not exist.
        """
        async with self._gateway():
            permissions = await self._permissions.get_list(cmd.permissions)

            role = await self._ensure.role_exists(cmd.role_id)
            await role.remove_permissions(permissions)
            await self._gateway.add(role)

            self._logger.debug("Permissions removed from role", role_id=role.id, role_name=role.name)
            return results.RoleInfo.from_model(role)
