import uuid

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.comment.conftest import another_hotel
from tests.fixtures.mocks import MockComment, MockHotel, MockUser


@pytest.fixture(autouse=True)
async def mock_data(
    save_instances,
    user,
    manager,
    hotel,
    sample_hotel,
    comment,
    sample_comment,
    another_hotel,
) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel, another_hotel]))
    await save_instances(MockComment([comment, sample_comment]))


@pytest.mark.anyio
class TestCommentAPI:
    async def test_add_comment_success(
        self, http_client: AsyncClient, valid_user_token, another_hotel
    ):
        """Test adding a new comment."""
        payload = {
            "hotel_id": str(another_hotel.id),
            "content": "API test comment",
            "rating": 5,
        }

        response = await http_client.post(
            "/api/v1/hotels/comments",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert isinstance(uuid.UUID(data["id"]), uuid.UUID)

    async def test_add_comment_without_rating(self, http_client: AsyncClient, valid_user_token, another_hotel):
        """Test adding comment without rating."""
        payload = {
            "hotel_id": str(another_hotel.id),
            "content": "Comment without rating",
        }

        response = await http_client.post(
            "/api/v1/hotels/comments",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    async def test_add_comment_already_exists(
        self, http_client: AsyncClient, valid_user_token, sample_hotel
    ):
        """Test adding an existing comment."""
        payload = {
            "hotel_id": str(sample_hotel.id),
            "content": "API test existing comment",
            "rating": 7,
        }

        response = await http_client.post(
            "/api/v1/hotels/comments",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_add_comment_unauthorized(self, http_client: AsyncClient, hotel):
        """Test adding comment without authorization."""
        payload = {
            "hotel_id": str(hotel.id),
            "content": "Unauthorized comment",
            "rating": 3,
        }

        response = await http_client.post("/api/v1/hotels/comments", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_comment_by_id_success(self, http_client: AsyncClient, valid_user_token, sample_comment):
        """Test getting comment by ID."""
        response = await http_client.get(
            f"/api/v1/hotels/comments/{sample_comment.id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_comment.id)
        assert data["content"] == sample_comment.content

    async def test_get_comment_by_id_not_found(self, http_client: AsyncClient, valid_user_token):
        """Test getting non-existent comment."""
        comment_id = uuid.uuid4()
        response = await http_client.get(
            f"/api/v1/hotels/comments/{comment_id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_comment_unauthorized(self, http_client: AsyncClient, sample_comment):
        """Test getting comment without authorization."""
        response = await http_client.get(
            f"/api/v1/hotels/comments/{sample_comment.id}"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_comment_success(self, http_client: AsyncClient, valid_user_token, sample_comment):
        """Test updating comment."""
        payload = {
            "content": "Updated via API",
            "rating": 2,
        }

        response = await http_client.patch(
            f"/api/v1/hotels/comments/{sample_comment.id}",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_comment.id)

    async def test_update_comment_partial(self, http_client: AsyncClient, valid_user_token, sample_comment):
        """Test partial comment update."""
        payload = {
            "content": "Only content updated via API",
        }

        response = await http_client.patch(
            f"/api/v1/hotels/comments/{sample_comment.id}",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_update_comment_not_found(self, http_client: AsyncClient, valid_user_token):
        """Test updating non-existent comment."""
        comment_id = uuid.uuid4()
        payload = {
            "content": "Should fail",
        }

        response = await http_client.patch(
            f"/api/v1/hotels/comments/{comment_id}",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_comment_unauthorized(self, http_client: AsyncClient, sample_comment):
        """Test updating comment without authorization."""
        payload = {
            "content": "Unauthorized update",
        }

        response = await http_client.patch(
            f"/api/v1/hotels/comments/{sample_comment.id}",
            json=payload,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_comment_success(self, http_client: AsyncClient, valid_user_token, comment):
        """Test deleting comment."""
        response = await http_client.delete(
            f"/api/v1/hotels/comments/{comment.id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(comment.id)

    async def test_delete_comment_not_found(self, http_client: AsyncClient, valid_user_token):
        """Test deleting non-existent comment."""
        comment_id = uuid.uuid4()

        response = await http_client.delete(
            f"/api/v1/hotels/comments/{comment_id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_comment_unauthorized(self, http_client: AsyncClient, sample_comment):
        """Test deleting comment without authorization."""
        response = await http_client.delete(
            f"/api/v1/hotels/comments/{sample_comment.id}"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
