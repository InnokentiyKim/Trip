import pytest
from fastapi import status
from httpx import AsyncClient

from tests.fixtures.mocks import MockUser


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
class TestUserAPI:
    async def test_get_user_info_success(
        self,
        http_client: AsyncClient,
        valid_user_token: str,
    ):
        """Test getting user info."""
        response = await http_client.get(
            "/api/v1/users/info",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert data["email"] == "test_user@mail.com"

    async def test_get_user_info_unauthorized(self, http_client: AsyncClient):
        """Test getting user info without authorization."""
        response = await http_client.get("/api/v1/users/info")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_user_info_invalid_token(
        self,
        http_client: AsyncClient,
        invalid_user_token: str,
    ):
        """Test getting user info with invalid token."""
        response = await http_client.get(
            "/api/v1/users/info",
            headers={"Authorization": f"Bearer {invalid_user_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_user_info_expired_token(
        self,
        http_client: AsyncClient,
        expired_user_token: str,
    ):
        """Test getting user info with expired token."""
        response = await http_client.get(
            "/api/v1/users/info",
            headers={"Authorization": f"Bearer {expired_user_token}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
