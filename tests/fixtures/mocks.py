from abc import ABC
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.authentication.session.application.interfaces.gateway import (
    AuthSessionGatewayProto,
    OTPCodeGatewayProto,
    PasswordResetTokenGatewayProto,
)
from src.apps.authentication.session.domain.models import (
    AuthSession,
    OTPCode,
    PasswordResetToken,
)
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.domain.models import User
from src.apps.authorization.access.domain.models import Permission, Role
from src.apps.authorization.role.application.interfaces.gateway import (
    PermissionGatewayProto,
    RoleGatewayProto,
)
from src.apps.comment.application.interfaces.gateway import CommentGatewayProto
from src.apps.comment.domain.models import Comment
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.file_object.application.interfaces.gateway import (
    FileObjectGatewayProto,
)
from src.apps.hotel.file_object.domain.models import FileObject
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.rooms.application.interfaces.gateway import RoomGatewayProto
from src.apps.hotel.rooms.domain.models import Room
from src.common.interfaces import GatewayProto

Model = TypeVar("Model")


class MockAlchemyDataMixin[Model]:
    """Mixin for saving mock data using SQLAlchemy AsyncSession."""

    instances: list[Model] = []

    async def save_by_session(self, session: AsyncSession) -> None:
        """Save instances to the database using the provided session."""
        async with session.begin():
            session.add_all(self.instances)


class MockData[Model](ABC):
    """Abstract base class for mock data handling."""

    gateway_proto: GatewayProto

    def __init__(self, instances: list[Model] | None = None) -> None:
        self.instances = instances or []

    async def save_by_gateway(self, gateway: GatewayProto) -> None:
        """Save instances using the provided gateway."""
        for instance in self.instances:
            await gateway.add(instance)


class MockAuthSession(MockAlchemyDataMixin[AuthSession], MockData[AuthSession]):
    """Mock data for AuthSession model."""

    gateway_proto = AuthSessionGatewayProto


class MockPasswordReset(MockAlchemyDataMixin[PasswordResetToken], MockData[PasswordResetToken]):
    """Mock data for PasswordResetToken model."""

    gateway_proto = PasswordResetTokenGatewayProto


class MockOTPCode(MockAlchemyDataMixin[OTPCode], MockData[OTPCode]):
    """Mock data for OTPCode model."""

    gateway_proto = OTPCodeGatewayProto


class MockUser(MockAlchemyDataMixin[User], MockData[User]):
    """Mock data for User model."""

    gateway_proto = UserGatewayProto


class MockRole(MockAlchemyDataMixin[Role], MockData[Role]):
    """Mock data for Role model."""

    gateway_proto = RoleGatewayProto


class MockPermission(MockAlchemyDataMixin[Permission], MockData[Permission]):
    """Mock data for Permission model."""

    gateway_proto = PermissionGatewayProto


class MockComment(MockAlchemyDataMixin[Comment], MockData[Comment]):
    """Mock data for Comment model."""

    gateway_proto = CommentGatewayProto


class MockBooking(MockAlchemyDataMixin[Booking], MockData[Booking]):
    """Mock data for Booking model."""

    gateway_proto = BookingGatewayProto


class MockFileObject(MockAlchemyDataMixin[FileObject], MockData[FileObject]):
    """Mock data for FileObject model."""

    gateway_proto = FileObjectGatewayProto


class MockHotel(MockAlchemyDataMixin[Hotel], MockData[Hotel]):
    """Mock data for Hotel model."""

    gateway_proto = HotelGatewayProto


class MockRoom(MockAlchemyDataMixin[Room], MockData[Room]):
    """Mock data for Room model."""

    gateway_proto = RoomGatewayProto
