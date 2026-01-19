import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from fastapi import status

from tests.fixtures.mocks import MockBooking, MockUser, MockHotel, MockRoom


@pytest.fixture(autouse=True)
async def mock_data(
    save_instances,
    user,
    manager,
    hotel,
    rooms,
    sample_hotel,
    sample_room,
    existing_room,
    sample_booking,
    confirmed_booking,
    bookings,
) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel]))
    await save_instances(MockRoom([*rooms, sample_room, existing_room]))
    await save_instances(MockBooking([sample_booking, confirmed_booking, *bookings]))


@pytest.mark.anyio
class TestBookingAPI:
    async def test_get_bookings(
        self, http_client: AsyncClient, valid_user_token, bookings
    ):
        """Test getting list of bookings."""
        response = await http_client.get(
            "/api/v1/bookings",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_booking_by_id_success(
        self, http_client: AsyncClient, valid_user_token, sample_booking
    ):
        """Test getting booking by id."""
        response = await http_client.get(
            f"/api/v1/bookings/{sample_booking.id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_booking.id)
        assert data["room_id"] == str(sample_booking.room_id)

    async def test_get_booking_by_id_not_found(
        self, http_client: AsyncClient, valid_user_token
    ):
        """Test getting non-existent booking."""
        booking_id = uuid.uuid4()
        response = await http_client.get(
            f"/api/v1/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_booking_success(
        self, http_client: AsyncClient, valid_user_token, existing_room
    ):
        """Test creating a new booking."""
        today = date.today()
        payload = {
            "room_id": str(existing_room.id),
            "date_from": str(today + timedelta(days=20)),
            "date_to": str(today + timedelta(days=25)),
        }

        response = await http_client.post(
            "/api/v1/bookings",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        data = response.json()
        assert "id" in data
        assert isinstance(uuid.UUID(data["id"]), uuid.UUID)

    async def test_create_booking_invalid_dates(
        self, http_client: AsyncClient, valid_user_token, sample_room
    ):
        """Test creating booking with invalid dates."""
        today = date.today()
        payload = {
            "room_id": str(sample_room.id),
            "date_from": str(today + timedelta(days=10)),
            "date_to": str(today + timedelta(days=5)),
        }

        response = await http_client.post(
            "/api/v1/bookings",
            json=payload,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_booking_unauthorized(
        self, http_client: AsyncClient, sample_room
    ):
        """Test creating booking without authorization."""
        today = date.today()
        payload = {
            "room_id": str(sample_room.id),
            "date_from": str(today + timedelta(days=1)),
            "date_to": str(today + timedelta(days=5)),
        }

        response = await http_client.post("/api/v1/bookings", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_cancel_booking_success(
        self, http_client: AsyncClient, valid_user_token, sample_booking
    ):
        """Test cancelling booking."""
        response = await http_client.post(
            f"/api/v1/bookings/{sample_booking.id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_booking.id)

    async def test_cancel_booking_not_found(
        self, http_client: AsyncClient, valid_user_token
    ):
        """Test cancelling non-existent booking."""
        booking_id = uuid.uuid4()
        response = await http_client.post(
            f"/api/v1/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_cancel_booking_unauthorized(
        self, http_client: AsyncClient, sample_booking
    ):
        """Test cancelling booking without authorization."""
        response = await http_client.post(f"/api/v1/bookings/{sample_booking.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_bookings_with_filters(
        self, http_client: AsyncClient, valid_user_token, sample_room
    ):
        """Test filtering bookings."""
        today = date.today()

        params = {
            "room_id": str(sample_room.id),
            "date_from": (today + timedelta(days=1)).isoformat(),
            "date_to": (today + timedelta(days=10)).isoformat(),
            "status": "pending",
        }

        response = await http_client.get(
            "/api/v1/bookings",
            params=params,
            headers={"Authorization": f"Bearer {valid_user_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
