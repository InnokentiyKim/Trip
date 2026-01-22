from uuid import uuid4

import pytest
from pydantic import SecretStr

from src.apps.authentication.user.adapters.adapter import UserAdapter
from src.apps.authentication.user.application import exceptions
from src.apps.authentication.user.application.service import UserService
from src.apps.authentication.user.domain import commands
from src.apps.authentication.user.domain.enums import UserTypeEnum
from src.apps.authentication.user.domain.fetches import GetUserInfo
from tests.fixtures.mocks import MockUser


@pytest.fixture
async def user_service(request_container) -> UserService:
    """Create a user service for testing."""
    return await request_container.get(UserService)


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
    await save_instances(MockUser([user, manager, sample_user, another_user, inactive_user]))


@pytest.mark.anyio
class TestUserService:
    async def test_create_new_user_success(self, user_service):
        """Test creating a new user."""
        cmd = commands.CreateUserCommand(
            email="newuser@mail.com",
            password=SecretStr("Password123"),
            user_type=UserTypeEnum.USER,
            name="New User",
            phone="+1111111111",
            avatar_url=None,
            is_active=True,
        )

        result = await user_service.create_new_user(cmd)

        assert result is not None
        assert result.email == "newuser@mail.com"
        assert result.name == "New User"

    async def test_create_new_user_already_exists(self, user_service, sample_user):
        """Test creating user with existing email."""
        cmd = commands.CreateUserCommand(
            email=sample_user.email,
            password=SecretStr("Password123"),
            user_type=UserTypeEnum.USER,
            name="Duplicate User",
            phone=None,
            avatar_url=None,
        )

        with pytest.raises(exceptions.UserAlreadyExistsError):
            await user_service.create_new_user(cmd)

    async def test_verify_user_credentials_success(self, user_service, sample_user):
        """Test verifying user credentials."""
        cmd = commands.VerifyUserCredentialsCommand(
            email=sample_user.email,
            password=SecretStr("Password123"),
        )

        result = await user_service.verify_user_credentials(cmd)

        assert result is not None
        assert result.email == sample_user.email

    async def test_verify_user_credentials_wrong_password(self, user_service, sample_user):
        """Test verifying credentials with wrong password."""
        cmd = commands.VerifyUserCredentialsCommand(
            email=sample_user.email,
            password=SecretStr("WrongPassword"),
        )

        with pytest.raises(exceptions.InvalidCredentialsError):
            await user_service.verify_user_credentials(cmd)

    async def test_verify_user_credentials_user_not_found(self, user_service):
        """Test verifying credentials for non-existent user."""
        cmd = commands.VerifyUserCredentialsCommand(
            email="nonexistent@mail.com",
            password=SecretStr("Password123"),
        )

        with pytest.raises(exceptions.UserNotFoundError):
            await user_service.verify_user_credentials(cmd)

    async def test_get_user_info_success(self, user_service, sample_user):
        """Test getting user info by ID."""
        fetch = GetUserInfo(user_id=sample_user.id)
        result = await user_service.get_user_info(fetch)

        assert result.id == sample_user.id
        assert result.email == sample_user.email

    async def test_get_user_info_not_found(self, user_service):
        """Test getting non-existent user info."""
        user_id = uuid4()
        fetch = GetUserInfo(user_id=user_id)

        with pytest.raises(exceptions.UserNotFoundError):
            await user_service.get_user_info(fetch)
