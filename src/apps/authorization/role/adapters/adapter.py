from uuid import UUID

from src.apps.authentication.user.domain.models import User
from src.apps.authorization.access.domain.models import Role, Permission
from src.apps.authorization.role.application.interfaces.gateway import RoleGatewayProto, PermissionGatewayProto
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.adapters.adapter import SQLAlchemyGateway, FakeGateway
from sqlalchemy import select, delete


class RoleAdapter(SQLAlchemyGateway, RoleGatewayProto):
    async def add(self, role: Role) -> None:
        """
        Adds a new role to the database.

        Args:
            role (Role): The role entity to be added.

        Returns:
            None
        """
        self.session.add(role)

    async def get(self, role_id: UUID) -> Role | None:
        """
        Retrieves a role from the database by its unique role_code.

        Args:
            role_id (str): The unique code of the role.

        Returns:
            Role | None: The Role object if found, otherwise None.
        """
        query_result = await self.session.execute(select(Role).filter_by(id=role_id))
        return query_result.scalars().first()

    async def get_by_name(self, role_name: UserRoleEnum) -> Role | None:
        """
        Retrieves a role from the database by its unique name.

        Args:
            role_name (str): The unique name of the role.

        Returns:
            Role | None: The Role object if found, otherwise None.
        """
        query_result = await self.session.execute(select(Role).filter_by(name=role_name))
        return query_result.scalars().first()

    async def get_all_users_granted_to_role(self, role_id: UUID) -> list[UUID]:
        """
        Retrieves all user IDs granted to the specified role.

        Args:
            role_id (UUID): The unique identifier of the role.

        Returns:
            list[UUID]: A list of user IDs granted to the role.
        """
        query = select(User.id).join(User.role).where(Role.id == role_id)
        query_result = await self.session.execute(query)
        return list(query_result.scalars().all())

    async def delete(self, role_id: UUID) -> bool:
        """
        Deletes a role from the database by its unique identifier.

        Args:
            role_id (UUID): The unique identifier of the role to delete.

        Returns:
            bool: True if the role was deleted, False if the role was not found.
        """
        stmt = delete(Role).where(Role.id == role_id)
        removed_info = await self.session.execute(stmt)
        return removed_info.rowcount != 0


class PermissionsAdapter(SQLAlchemyGateway, PermissionGatewayProto):
    async def add(self, permission: Permission) -> None:
        """Adds a new permission to the database."""
        self.session.add(permission)

    async def list_all_permissions(self) -> list[Permission]:
        """
        Returns a list of permission names associated with the specified role.

        Returns:
            RolePermissionsListReturn: A list of permission names linked to the role.
        """
        query = select(*Permission.returning_columns())
        query_result = await self.session.execute(query)
        return list(query_result.scalars().all())

    async def get_list(self, permission_ids: list[UUID]) -> list[Permission]:
        """
        Returns a list of permission IDs from the input list that are not found in the database.

        Args:
            permission_ids (list[UUID]): List of permission UUIDs to check.

        Returns:
            list[Permission]: List of Permissions
        """
        query = select(Permission).where(Permission.id.in_(permission_ids))
        query_result = await self.session.execute(query)
        return list(query_result.scalars().all())


class FakeRoleAdapter(FakeGateway[Role], RoleGatewayProto):
    async def add(self, role: Role) -> None:
        """
        Adds a new role to the database.

        Args:
            role (Role): The role entity to be added.

        Returns:
            None
        """
        self._collection.add(role)

    async def get(self, role_id: UUID) -> Role | None:
        """
        Retrieves a role from the database by its unique role_code.

        Args:
            role_id (str): The unique code of the role.

        Returns:
            Role | None: The Role object if found, otherwise None.
        """
        return next((role for role in self._collection if role.id == role_id), None)

    async def get_by_name(self, role_name: UserRoleEnum) -> Role | None:
        """
        Retrieves a role from the database by its unique name.

        Args:
            role_name (str): The unique name of the role.

        Returns:
            Role | None: The Role object if found, otherwise None.
        """
        return next((role for role in self._collection if role.name == role_name), None)

    async def get_all_users_granted_to_role(self, role_id: UUID) -> list[UUID]:
        """
        Retrieves all user IDs granted to the specified role.

        Args:
            role_id (UUID): The unique identifier of the role.

        Returns:
            list[UUID]: A list of user IDs granted to the role.
        """
        users = (role.users for role in self._collection if role.id == role_id)
        return [user.id for user in users]

    async def delete(self, role_id: UUID) -> bool:
        """
        Deletes a role from the database by its unique identifier.

        Args:
            role_id (UUID): The unique identifier of the role to delete.

        Returns:
            bool: True if the role was deleted, False if the role was not found.
        """
        role = next((role for role in self._collection if role.id == role_id))
        if role is None:
            return False

        self._collection.discard(role)
        return True


class FakePermissionsAdapter(FakeGateway, PermissionGatewayProto):
    async def add(self, permission: Permission) -> None:
        """Adds a new permission to the database."""
        self._collection.add(permission)

    async def list_all_permissions(self) -> list[Permission]:
        """
        Returns a list of permission names associated with the specified role.

        Returns:
            RolePermissionsListReturn: A list of permission names linked to the role.
        """
        return list(self._collection)

    async def get_list(self, permission_ids: list[UUID]) -> list[Permission]:
        """
        Returns a list of permission IDs from the input list that are not found in the database.

        Args:
            permission_ids (list[UUID]): List of permission UUIDs to check.

        Returns:
            list[Permission]: List of Permissions
        """
        return [
            permission for permission in self._collection if permission.id in permission_ids
        ]
