import uuid

import pytest
from httpx import AsyncClient
from fastapi import status
from tests.fixtures.mocks import MockUser, MockHotel


@pytest.fixture(autouse=True)
async def mock_data(save_instances, user, manager, hotel) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel]))


@pytest.mark.asyncio
class TestHotelAPI:
    async def test_get_hotels(self, http_client: AsyncClient, hotel):
        """Test getting list of hotels."""
        response = await http_client.get("/api/v1/hotels")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_hotel_by_id_success(self, http_client: AsyncClient, hotel):
        """Test getting hotel by id."""
        response = await http_client.get(f"/api/v1/hotels/{hotel.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(hotel.id)
        assert data["name"] == hotel.name

    async def test_get_hotel_by_id_not_found(self, http_client: AsyncClient):
        """Test getting non-existent hotel."""
        hotel_id = uuid.uuid4()
        response = await http_client.get(f"/api/v1/hotels/{hotel_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_hotel_success(self, http_client: AsyncClient, valid_manager_token):
        """Test creating a new hotel."""
        payload = {
            "name": "New Test Hotel",
            "location": "New Test Location",
            "rooms_quantity": 50,
            "is_active": True,
            "services": {"WiFi": True, "Parking": True},
            "image_id": None,
        }

        response = await http_client.post(
            "/api/v1/hotels",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        data = response.json()
        assert "id" in data
        assert isinstance(uuid.UUID(data["id"]), uuid.UUID)

    async def test_create_hotel_unauthorized(self, http_client: AsyncClient):
        """Test creating hotel without authorization."""
        payload = {
            "name": "Unauthorized Hotel",
            "location": "Test Location",
            "rooms_quantity": 10,
            "is_active": True,
        }

        response = await http_client.post("/api/v1/hotels", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_hotel_forbidden(self, http_client: AsyncClient, valid_user_token):
        """Test creating hotel without required permissions."""
        payload = {
            "name": "Forbidden Hotel",
            "location": "Test Location",
            "rooms_quantity": 10,
            "is_active": True,
        }

        response = await http_client.post(
            "/api/v1/hotels",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_hotel_already_exists(self, http_client: AsyncClient, valid_manager_token, hotel):
        """Test creating hotel with duplicate name."""
        payload = {
            "name": hotel.name,
            "location": hotel.location,
            "rooms_quantity": hotel.rooms_quantity,
            "is_active": True,
        }

        response = await http_client.post(
            "/api/v1/hotels",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_update_hotel_success(self, http_client: AsyncClient, valid_manager_token, hotel):
        """Test updating hotel."""
        payload = {
            "hotel_id": str(hotel.id),
            "name": "Updated Hotel Name",
            "location": hotel.location,
            "rooms_quantity": 100,
            "is_active": True,
        }

        response = await http_client.patch(
            "/api/v1/hotels",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(hotel.id)

    async def test_update_hotel_not_found(self, http_client: AsyncClient, valid_manager_token):
        """Test updating non-existent hotel."""
        hotel_id = uuid.uuid4()
        payload = {
            "hotel_id": str(hotel_id),
            "name": "Updated Name",
            "location": "Test Location",
            "rooms_quantity": 50,
            "is_active": True,
        }

        response = await http_client.patch(
            "/api/v1/hotels",
            json=payload,
            headers={"Authorization": f"Bearer {valid_manager_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_hotel_unauthorized(self, http_client: AsyncClient, hotel):
        """Test updating hotel without authorization."""
        payload = {
            "hotel_id": str(hotel.id),
            "name": "Updated Name",
            "location": hotel.location,
            "rooms_quantity": 50,
            "is_active": True,
        }

        response = await http_client.patch("/api/v1/hotels", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_hotel_forbidden(self, http_client: AsyncClient, valid_user_token, hotel):
        """Test updating hotel without required permissions."""
        payload = {
            "hotel_id": str(hotel.id),
            "name": "Updated Name",
            "location": hotel.location,
            "rooms_quantity": 50,
            "is_active": True,
        }

        response = await http_client.patch(
            "/api/v1/hotels",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_hotels_with_filters(self, http_client: AsyncClient, hotel):
        """Test filtering hotels."""
        response = await http_client.get(
            "/api/v1/hotels",
            params={"location": hotel.location}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert all(h["location"] == hotel.location for h in data)
