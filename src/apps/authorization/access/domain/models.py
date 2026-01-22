import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.authorization.access.domain.enums import (
    ResourceTypeEnum,
    UserPermissionEnum,
)
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.domain.models import Base

if TYPE_CHECKING:
    from src.apps.authentication.user.domain.models import User  # noqa: F401


class AuthorizationBase(Base):
    __abstract__ = True


class Permission(AuthorizationBase):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("name", "resource_type", name="uq_permission_name_resource"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    name: Mapped[UserPermissionEnum] = mapped_column(
        SAEnum(
            UserPermissionEnum,
            name="user_permission_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [permission.value for permission in enum_cls],
        ),
        nullable=False,
    )
    resource_type: Mapped[ResourceTypeEnum] = mapped_column(
        SAEnum(
            ResourceTypeEnum,
            name="resource_type_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [resource_type.value for resource_type in enum_cls],
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)

    def __init__(
        self,
        name: UserPermissionEnum,
        resource_type: ResourceTypeEnum,
        description: str | None = None,
    ) -> None:
        super().__init__()
        self.id = uuid.uuid4()
        self.name = name
        self.resource_type = resource_type
        self.description = description

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
        default=UserRoleEnum.USER,
    )
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)

    permissions: Mapped[list[Permission]] = relationship(  # noqa: F821
        "Permission",
        secondary="role_permissions",
        lazy="selectin",
        cascade="all",
    )

    users: Mapped[list["User"]] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
        uselist=True,
    )

    def __init__(
        self,
        name: UserRoleEnum,
        description: str | None = None,
        permissions: list[Permission] | None = None,
        users: list["User"] | None = None,
    ) -> None:
        super().__init__()
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.permissions = permissions or []
        self.users = users or []

    @classmethod
    def returning_columns(cls) -> list[Any]:
        """Returns the list of columns to be selected."""
        return list(cls.__table__.columns)

    async def add_permissions(self, permissions: list[Permission]) -> None:
        """Add permissions to the role_id."""
        self_permissions = await self.awaitable_attrs.permissions
        for permission in permissions:
            if permission not in self_permissions:
                self.permissions.append(permission)

    async def remove_permissions(self, permissions: list[Permission]) -> None:
        """Remove permissions from the role_id."""
        self_permissions = await self.awaitable_attrs.permissions

        for permission in permissions:
            if permission in self_permissions:
                self.permissions.remove(permission)
