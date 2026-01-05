from uuid import UUID

from src.apps.authorization.access.application.interfaces.gateway import AccessGatewayProto
from src.apps.authorization.access.domain.models import Permission, RolePermissions, Role
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.rooms.domain.models import Room
from src.common.adapters.adapter import SQLAlchemyGateway, FakeGateway
from src.apps.authorization.access.domain.enums import PermissionEnum, ResourceTypeEnum
from sqlalchemy import select
from src.apps.authorization.access.domain import exceptions


resource_model_map = {
    ResourceTypeEnum.HOTEL: Hotel,
    ResourceTypeEnum.ROOM: Room,
    ResourceTypeEnum.BOOKING: Booking,
}


class AccessAdapter(SQLAlchemyGateway, AccessGatewayProto):
    async def _get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """
        Retrieve all permissions associated with role.

        Args:
            role_id (UUID): The unique identifier of the role.

        Returns:
            list[Permission]: A list of Permission objects associated with the user.
        """
        stmt = (
            select(Permission)
            .join(RolePermissions, Permission.id == RolePermissions.permission_id)
            .where(RolePermissions.role_id == role_id)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars())

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
        obj_model = resource_model_map.get(object_type)
        if not obj_model:
            raise exceptions.UnknownResourceTypeError

        resource = await self.get_one_item(obj_model, id=object_id)
        if not resource:
            raise exceptions.ResourceNotFoundError

        owner_id = getattr(resource, 'owner', None) or getattr(resource, 'user_id', None)
        if not owner_id:
            return False

        return owner_id == user_id

    async def check_object_access(
        self, user_id: UUID, user_role: UUID, object_type: ResourceTypeEnum, object_id: UUID
    ) -> bool:
        """
        Check if a user has access to a specific object.

        Args:
            user_id (UUID): The unique identifier of the user.
            user_role (UUID): The unique identifier of the user's role.
            object_type (ResourceTypeEnum): The type of the object.
            object_id (UUID | int): The unique identifier of the object.

        Returns:
            bool: True if the user has access, False otherwise.
        """
        role: Role = await self.get_one_item(Role, id=user_role)
        if role.name == UserRoleEnum.ADMIN:
            return True

        return await self.is_resource_owner(user_id, object_type, object_id)


    async def check_permission(self, role_id: UUID, resource_type: ResourceTypeEnum, permission: PermissionEnum) -> bool:
        """
        Check if a subject has a specific permission.

        Args:
            role_id (UUID): The unique identifier of the role.
            resource_type (ResourceTypeEnum): The type of the resource.
            permission (PermissionEnum): The permission to check.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """

        role_permissions = await self._get_role_permissions(role_id)
        if any(
            perm.name == permission and perm.resource_type == resource_type
            for perm in role_permissions
        ):
            return True

        return False


class FakeAccessAdapter(FakeGateway[RolePermissions], AccessGatewayProto):
    async def _get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """
        Retrieve all permissions associated with role.

        Args:
            role_id (UUID): The unique identifier of the role.

        Returns:
            list[Permission]: A list of Permission objects associated with the user.
        """
        pass

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
        pass

    async def check_object_access(
        self, user_id: UUID, user_role: UUID, object_type: ResourceTypeEnum, object_id: UUID
    ) -> bool:
        """
        Check if a user has access to a specific object.

        Args:
            user_id (UUID): The unique identifier of the user.
            user_role (UUID): The unique identifier of the user's role.
            object_type (ResourceTypeEnum): The type of the object.
            object_id (UUID | int): The unique identifier of the object.

        Returns:
            bool: True if the user has access, False otherwise.
        """
        pass


    async def check_permission(self, role_id: UUID, resource_type: ResourceTypeEnum, permission: PermissionEnum) -> bool:
        """
        Check if a subject has a specific permission.

        Args:
            role_id (UUID): The unique identifier of the role.
            resource_type (ResourceTypeEnum): The type of the resource.
            permission (PermissionEnum): The permission to check.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        pass
