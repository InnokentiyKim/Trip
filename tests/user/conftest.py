import pytest

from src.apps.authentication.user.domain.models import User
from src.apps.authorization.role.application.interfaces.gateway import RoleGatewayProto
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.interfaces import SecurityGatewayProto


@pytest.fixture
async def sample_user(request_container) -> User:
    """Create a sample user for testing."""
    role_gateway = await request_container.get(RoleGatewayProto)
    security_gateway = await request_container.get(SecurityGatewayProto)

    role = await role_gateway.get_by_name(UserRoleEnum.USER)
    hashed_password = await security_gateway.hash_password("Password123")

    return User(
        email="sample_user@mail.com",
        hashed_password=hashed_password,
        role_id=role.id,
        name="Sample User",
        phone="+1234567890",
    )


@pytest.fixture
async def another_user(request_container) -> User:
    """Create another user for testing."""
    role_gateway = await request_container.get(RoleGatewayProto)
    security_gateway = await request_container.get(SecurityGatewayProto)

    role = await role_gateway.get_by_name(UserRoleEnum.USER)
    hashed_password = await security_gateway.hash_password("Password456")

    return User(
        email="another_user@mail.com",
        hashed_password=hashed_password,
        role_id=role.id,
        name="Another User",
    )


@pytest.fixture
async def inactive_user(request_container) -> User:
    """Create an inactive user for testing."""
    role_gateway = await request_container.get(RoleGatewayProto)
    security_gateway = await request_container.get(SecurityGatewayProto)

    role = await role_gateway.get_by_name(UserRoleEnum.USER)
    hashed_password = await security_gateway.hash_password("Password789")

    return User(
        email="inactive_user@mail.com",
        hashed_password=hashed_password,
        role_id=role.id,
        name="Inactive User",
        is_active=False,
    )


@pytest.fixture
def users(sample_user, another_user, inactive_user) -> list[User]:
    """Create multiple users for testing."""
    return [sample_user, another_user, inactive_user]
