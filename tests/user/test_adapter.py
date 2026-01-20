import uuid

import pytest

from src.apps.authentication.user.adapters.adapter import UserAdapter
from src.apps.authentication.user.domain.models import User
from tests.fixtures.mocks import MockUser


@pytest.fixture
async def user_adapter(request_container) -> UserAdapter:
    """Create a user adapter for testing."""
    return await request_container.get(dependency_type=UserAdapter)


@pytest.fixture(autouse=True)
async def mock_data(
    save_instances,
    user,
    manager,
    sample_user,
    another_user,
    inactive_user,
) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(
        MockUser([user, manager, sample_user, another_user, inactive_user])
    )


@pytest.mark.anyio
class TestUserAdapter:
    """Tests for UserAdapter."""

    async def test_get_user_by_id_success(self, user_adapter, sample_user):
        """Test getting user by ID."""
        result = await user_adapter.get_user_by_id(sample_user.id)

        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email

    async def test_get_user_by_id_not_found(self, user_adapter):
        """Test getting non-existent user."""
        non_existent_id = uuid.uuid4()
        result = await user_adapter.get_user_by_id(non_existent_id)

        assert result is None

    async def test_get_user_by_email_success(self, user_adapter, sample_user):
        """Test getting user by email."""
        result = await user_adapter.get_user_by_email(sample_user.email)

        assert result is not None
        assert result.email == sample_user.email
        assert result.id == sample_user.id

    async def test_get_user_by_email_not_found(self, user_adapter):
        """Test getting non-existent user by email."""
        result = await user_adapter.get_user_by_email("nonexistent@mail.com")

        assert result is None

    async def test_get_user_by_phone_success(self, user_adapter, sample_user):
        """Test getting user by phone."""
        if sample_user.phone:
            result = await user_adapter.get_user_by_phone(sample_user.phone)

            assert result is not None
            assert result.phone == sample_user.phone
            assert result.id == sample_user.id

    async def test_get_user_by_phone_not_found(self, user_adapter):
        """Test getting non-existent user by phone."""
        result = await user_adapter.get_user_by_phone("+9999999999")

        assert result is None

    async def test_get_users_all(self, user_adapter, users):
        """Test getting all users."""
        result = await user_adapter.get_users()

        assert isinstance(result, list)
        assert len(result) >= len(users)
        assert all(isinstance(u, User) for u in result)

    async def test_get_users_with_filter(self, user_adapter, sample_user):
        """Test getting users with filter."""
        result = await user_adapter.get_users(email=sample_user.email)

        assert len(result) == 1
        assert result[0].email == sample_user.email

    async def test_add_user_success(self, user_adapter, request_container):
        """Test adding a new user."""
        from src.apps.authorization.role.application.interfaces.gateway import (
            RoleGatewayProto,
        )
        from src.apps.authorization.role.domain.enums import UserRoleEnum
        from src.common.interfaces import SecurityGatewayProto

        role_gateway = await request_container.get(RoleGatewayProto)
        security_gateway = await request_container.get(SecurityGatewayProto)

        role = await role_gateway.get_by_name(UserRoleEnum.USER)
        hashed_password = await security_gateway.hash_password("NewPassword123")

        new_user = User(
            email="new_user@mail.com",
            hashed_password=hashed_password,
            role_id=role.id,
            name="New User",
        )

        await user_adapter.add(new_user)

        result = await user_adapter.get_user_by_email("new_user@mail.com")
        assert result is not None
        assert result.email == "new_user@mail.com"

    async def test_update_user_success(self, user_adapter, sample_user):
        """Test updating user."""
        updated_id = await user_adapter.update_user(
            sample_user,
            name="Updated Name",
        )

        assert updated_id == sample_user.id

        updated_user = await user_adapter.get_user_by_id(sample_user.id)
        assert updated_user.name == "Updated Name"

    async def test_delete_user_success(self, user_adapter, request_container):
        """Test deleting user."""
        from src.apps.authorization.role.application.interfaces.gateway import (
            RoleGatewayProto,
        )
        from src.apps.authorization.role.domain.enums import UserRoleEnum
        from src.common.interfaces import SecurityGatewayProto

        role_gateway = await request_container.get(RoleGatewayProto)
        security_gateway = await request_container.get(SecurityGatewayProto)

        role = await role_gateway.get_by_name(UserRoleEnum.USER)
        hashed_password = await security_gateway.hash_password("TempPassword123")

        temp_user = User(
            email="temp_user@mail.com",
            hashed_password=hashed_password,
            role_id=role.id,
            name="Temp User",
        )

        await user_adapter.add(temp_user)
        await user_adapter.delete_user(temp_user)

        deleted_user = await user_adapter.get_user_by_id(temp_user.id)
        assert deleted_user is None
