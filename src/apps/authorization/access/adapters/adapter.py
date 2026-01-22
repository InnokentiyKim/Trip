from uuid import UUID

from sqlalchemy import select

from src.apps.authentication.user.domain.models import User
from src.apps.authorization.access.application.interfaces.gateway import (
    AccessGatewayProto,
)
from src.apps.authorization.access.domain import exceptions
from src.apps.authorization.access.domain.enums import PermissionEnum, ResourceTypeEnum
from src.apps.authorization.access.domain.models import (
    Permission,
    Role,
    RolePermissions,
)
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.apps.comment.domain.models import Comment
from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.rooms.domain.models import Room
from src.common.adapters.adapter import FakeGateway, SQLAlchemyGateway

resource_model_map = {
    resource_type: model
    for resource_type, model in [
        (ResourceTypeEnum.USER, User),
        (ResourceTypeEnum.HOTEL, Hotel),
        (ResourceTypeEnum.ROOM, Room),
        (ResourceTypeEnum.BOOKING, Booking),
        (ResourceTypeEnum.COMMENT, Comment),
    ]
}


class AccessAdapter(SQLAlchemyGateway, AccessGatewayProto):
    async def _get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """
        Retrieve all permissions associated with role_id.

        Args:
            role_id (UUID): The unique identifier of the role_id.

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
        obj_model = resource_model_map.get(object_type, None)

        if not obj_model:
            raise exceptions.UnknownResourceTypeError

        resource = await self.get_one_item(obj_model, id=object_id)
        if not resource:
            raise exceptions.ResourceNotFoundError

        owner_id = getattr(resource, "owner", None) or getattr(resource, "user_id", None)
        if not owner_id:
            return False

        return owner_id == user_id  # type: ignore

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
        role = await self.get_item_by_id(Role, user_role)

        if role.name == UserRoleEnum.ADMIN:  # type: ignore
            return True

        return await self.is_resource_owner(user_id, object_type, object_id)

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
        role_permissions = await self._get_role_permissions(role_id)
        if any(perm.name == permission and perm.resource_type == resource_type for perm in role_permissions):
            return True

        return False


class FakeAccessAdapter(FakeGateway[RolePermissions], AccessGatewayProto):
    async def _get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """
        Retrieve all permissions associated with role_id.

        Args:
            role_id (UUID): The unique identifier of the role_id.

        Returns:
            list[Permission]: A list of Permission objects associated with the user.
        """
        return []

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
        return True

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
        return True

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
        return True
