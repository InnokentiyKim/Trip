import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Enum as SAEnum, ForeignKey

from src.apps.authorization.access.domain.enums import UserPermissionEnum, ResourceTypeEnum
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.domain.models import Base


class AuthorizationBase(Base):
    __abstract__ = True


class Permission(AuthorizationBase):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    name: Mapped[UserPermissionEnum] = mapped_column(
        SAEnum(
            UserPermissionEnum,
            name="user_permission_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [permission.value for permission in enum_cls],
        ),
        nullable=False,
        unique=True
    )
    resource_type: Mapped[ResourceTypeEnum] = mapped_column(
        SAEnum(
            ResourceTypeEnum,
            name="resource_type_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [resource_type.value for resource_type in enum_cls],
        ),
        nullable=False
    )
    description: Mapped[str] = mapped_column(String(256), nullable=True)

    def __hash__(self) -> int:
        """Returns the hash of the object's id."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """True if the other object is a Permission and has the same name. False otherwise."""
        if not isinstance(other, Permission):
            raise NotImplementedError
        return self.name == other.name

    @classmethod
    def returning_columns(cls) -> list[Any]:
        """Returns the list of columns to be selected."""
        return list(cls.__table__.columns)


class RolePermissions(AuthorizationBase):
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )


class Role(AuthorizationBase, AsyncAttrs):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    name: Mapped[UserRoleEnum] = mapped_column(
        SAEnum(
            UserRoleEnum,
            name="user_role_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [role.value for role in enum_cls],
        ),
        nullable=False,
        unique=True,
        default=UserRoleEnum.USER
    )
    description: Mapped[str] = mapped_column(String(256), nullable=True)

    permissions: Mapped[list[Permission]] = relationship(  # noqa: F821
        "Permission",
        secondary="role_permissions",
        lazy="joined",
        cascade="all",
    )

    @classmethod
    def returning_columns(cls) -> list[Any]:
        """Returns the list of columns to be selected."""
        return list(cls.__table__.columns)

    async def add_permissions(self, permissions: list[Permission]) -> None:
        """Add permissions to the role."""
        self_permissions = await self.awaitable_attrs.permissions
        for permission in permissions:
            if permission not in self_permissions:
                self.permissions.append(permission)

    async def remove_permissions(self, permissions: list[Permission]) -> None:
        """Remove permissions from the role."""
        self_permissions = await self.awaitable_attrs.permissions
        for permission in permissions:
            if permission in self_permissions:
                self.permissions.remove(permission)
