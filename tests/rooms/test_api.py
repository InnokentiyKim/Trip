import uuid

import pytest
from httpx import AsyncClient
from fastapi import status

from tests.fixtures.mocks import MockRoom, MockUser, MockHotel


@pytest.fixture(autouse=True)
async def mock_data(save_instances, user, manager, hotel, rooms, sample_hotel, sample_room, existing_room) -> None:
    """Save required dependencies to database for tests."""
    print(f"\n[mock_data] Saving data for test...")
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel]))
    await save_instances(MockRoom([*rooms, sample_room, existing_room]))
    print(f"[mock_data] Saved: {len(rooms) + 2} rooms, 2 hotels, 2 users")


@pytest.mark.anyio
class TestRoomAPI:
    async def test_list_rooms(self, http_client: AsyncClient, hotel, rooms):
        """Test getting list of rooms."""
        response = await http_client.get(f"/api/v1/hotels/{hotel.id}/rooms")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_room_by_id_success(self, http_client: AsyncClient, sample_room):
        """Test getting room by id."""
        response = await http_client.get(f"/api/v1/hotels/rooms/{sample_room.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_room.id)
        assert data["name"] == sample_room.name

    async def test_get_room_by_id_not_found(self, http_client: AsyncClient):
        """Test getting non-existent room."""
        room_id = uuid.uuid4()
        response = await http_client.get(f"/api/v1/hotels/rooms/{room_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_room_success(self, http_client: AsyncClient, valid_manager_token, hotel):
        """Test creating a new room."""
        payload = {
            "name": "New Test Room",
            "hotel_id": str(hotel.id),
            "price": "100.00",
            "quantity": 5,
            "description": "Test room description",
            "services": {"WiFi": True, "TV": True},
            "image_id": None,
        }

        response = await http_client.post(
            f"/api/v1/hotels/{hotel.id}/rooms",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        data = response.json()
        assert "id" in data
        assert isinstance(uuid.UUID(data["id"]), uuid.UUID)
        assert data["hotel_id"] == str(hotel.id)

    async def test_add_room_unauthorized(self, http_client: AsyncClient, hotel):
        """Test creating room without authorization."""
        payload = {
            "name": "Unauthorized Room",
            "hotel_id": str(hotel.id),
            "price": "100.00",
            "quantity": 5,
            "description": "Test room description",
            "services": None,
            "image_id": None,
        }

        response = await http_client.post(
            f"/api/v1/hotels/{hotel.id}/rooms",
            json=payload,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_add_room_forbidden(self, http_client: AsyncClient, valid_user_token, hotel):
        """Test creating room without required permissions."""
        payload = {
            "name": "Forbidden Room",
            "hotel_id": str(hotel.id),
            "price": "100.00",
            "quantity": 5,
            "description": "Test room description",
            "services": {"WiFi": True, "TV": True},
            "image_id": None,
        }

        response = await http_client.post(
            f"/api/v1/hotels/{hotel.id}/rooms",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_add_room_already_exists(
        self, http_client: AsyncClient, valid_manager_token, sample_hotel, existing_room
    ):
        """Test creating room with duplicate name."""
        payload = {
            "name": existing_room.name,
            "hotel_id": str(existing_room.hotel_id),
            "price": "100.00",
            "quantity": 5,
            "description": "Test room description",
            "services": None,
            "image_id": None,
        }

        response = await http_client.post(
            f"/api/v1/hotels/{sample_hotel.id}/rooms",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_update_room_success(self, http_client: AsyncClient, valid_manager_token, sample_room):
        """Test updating room."""
        payload = {
            "name": "Updated Room Name",
            "price": "150.00",
            "quantity": 10,
        }

        response = await http_client.patch(
            f"/api/v1/hotels/rooms/{sample_room.id}",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_room.id)

    async def test_update_room_not_found(self, http_client: AsyncClient, valid_manager_token):
        """Test updating non-existent room."""
        room_id = uuid.uuid4()
        payload = {
            "name": "Updated Name",
            "price": "150.00",
        }

        response = await http_client.patch(
            f"/api/v1/hotels/rooms/{room_id}",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_room_unauthorized(self, http_client: AsyncClient, sample_room):
        """Test updating room without authorization."""
        payload = {
            "name": "Updated Name",
            "price": "150.00",
        }

        response = await http_client.patch(
            f"/api/v1/hotels/rooms/{sample_room.id}",
            json=payload,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_room_forbidden(self, http_client: AsyncClient, valid_user_token, sample_room):
        """Test updating room without required permissions."""
        payload = {
            "name": "Updated Name",
            "price": "150.00",
        }

        response = await http_client.patch(
            f"/api/v1/hotels/rooms/{sample_room.id}",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_room_success(self, http_client: AsyncClient, valid_manager_token, sample_room):
        """Test deleting room."""
        response = await http_client.delete(
            f"/api/v1/hotels/rooms/{sample_room.id}",
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code in  (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK)
        # Verify deletion
        get_response = await http_client.get(f"/api/v1/hotels/rooms/{sample_room.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_room_not_found(self, http_client: AsyncClient, valid_manager_token):
        """Test deleting non-existent room."""
        room_id = uuid.uuid4()
        response = await http_client.delete(
            f"/api/v1/hotels/rooms/{room_id}",
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_room_unauthorized(self, http_client: AsyncClient, sample_room):
        """Test deleting room without authorization."""
        response = await http_client.delete(f"/api/v1/hotels/rooms/{sample_room.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_room_forbidden(self, http_client: AsyncClient, valid_user_token, sample_room):
        """Test deleting room without required permissions."""
        response = await http_client.delete(
            f"/api/v1/hotels/rooms/{sample_room.id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_rooms_with_filters(self, http_client: AsyncClient, hotel, sample_room):
        """Test filtering rooms by price range."""
        response = await http_client.get(
            f"/api/v1/hotels/{hotel.id}/rooms",
            params={"price_from": "50", "price_to": "200"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
