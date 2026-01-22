import uuid

import pytest

from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from src.apps.hotel.hotels.domain.models import Hotel
from tests.fixtures.mocks import MockHotel, MockUser


@pytest.fixture
async def hotel_adapter(request_container) -> HotelGatewayProto:
    """Create a hotel adapter for testing."""
    return await request_container.get(dependency_type=HotelGatewayProto)


@pytest.fixture(autouse=True)
async def mock_data(save_instances, user, manager, hotel) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel]))


@pytest.mark.asyncio
class TestHotelAdapter:
    async def test_get_hotels_all(self, hotel_adapter, hotel):
        """Test getting all hotels."""
        hotels = await hotel_adapter.get_hotels()

        assert isinstance(hotels, list)
        assert len(hotels) >= 1
        assert all(isinstance(h, Hotel) for h in hotels)

    async def test_get_hotels_with_filters(self, hotel_adapter, hotel):
        """Test getting hotels with filters."""
        hotels = await hotel_adapter.get_hotels(location=hotel.location)

        assert len(hotels) >= 1
        assert all(h.location == hotel.location for h in hotels)

    async def test_get_hotels_only_active(self, hotel_adapter, manager):
        """Test getting only active hotels."""
        inactive_hotel = Hotel(
            name="Inactive Hotel",
            location="Test Location",
            rooms_quantity=10,
            owner=manager.id,
            is_active=False,
            services=None,
        )
        await hotel_adapter.add(inactive_hotel)

        hotels = await hotel_adapter.get_hotels(only_active=True)

        assert all(h.is_active for h in hotels)

    async def test_get_hotel_by_id_success(self, hotel_adapter, hotel):
        """Test getting hotel by id."""
        result = await hotel_adapter.get_hotel_by_id(hotel.id)

        assert result is not None
        assert result.id == hotel.id
        assert result.name == hotel.name

    async def test_get_hotel_by_id_not_found(self, hotel_adapter):
        """Test getting non-existent hotel."""
        result = await hotel_adapter.get_hotel_by_id(uuid.uuid4())

        assert result is None

    async def test_get_users_hotel_success(self, hotel_adapter, hotel, manager):
        """Test getting user's hotel."""
        result = await hotel_adapter.get_users_hotel(manager.id, hotel.id)

        assert result is not None
        assert result.id == hotel.id
        assert result.owner == manager.id

    async def test_get_users_hotel_wrong_owner(self, hotel_adapter, hotel, user):
        """Test getting hotel with wrong owner."""
        result = await hotel_adapter.get_users_hotel(user.id, hotel.id)

        assert result is None

    async def test_add_hotel_success(self, hotel_adapter, manager):
        """Test adding a new hotel."""
        new_hotel = Hotel(
            name="New Test Hotel",
            location="New Location",
            rooms_quantity=25,
            owner=manager.id,
            services={"wifi": True},
        )

        hotel_id = await hotel_adapter.add(new_hotel)

        assert hotel_id is not None
        assert isinstance(hotel_id, uuid.UUID)

    async def test_add_hotel_duplicate_name(self, hotel_adapter, hotel, manager):
        """Test adding hotel with duplicate name."""
        duplicate_hotel = Hotel(
            name=hotel.name,
            location=hotel.location,
            rooms_quantity=10,
            owner=manager.id,
            services=None,
        )

        hotel_id = await hotel_adapter.add(duplicate_hotel)

        assert hotel_id is None

    async def test_update_hotel_success(self, hotel_adapter, hotel):
        """Test updating hotel."""
        updated_id = await hotel_adapter.update_hotel(
            hotel,
            name="Updated Name",
            rooms_quantity=100,
        )

        assert updated_id == hotel.id

        updated_hotel = await hotel_adapter.get_hotel_by_id(hotel.id)
        assert updated_hotel.name == "Updated Name"
        assert updated_hotel.rooms_quantity == 100

    async def test_update_hotel_partial(self, hotel_adapter, hotel):
        """Test partial update of hotel."""
        original_name = hotel.name

        updated_id = await hotel_adapter.update_hotel(
            hotel,
            rooms_quantity=150,
        )

        assert updated_id == hotel.id

        updated_hotel = await hotel_adapter.get_hotel_by_id(hotel.id)
        assert updated_hotel.name == original_name
        assert updated_hotel.rooms_quantity == 150

    async def test_delete_hotel_success(self, hotel_adapter, manager):
        """Test deleting hotel."""
        new_hotel = Hotel(
            name="Hotel to Delete",
            location="Test Location",
            rooms_quantity=10,
            owner=manager.id,
            services=None,
        )
        hotel_id = await hotel_adapter.add(new_hotel)

        await hotel_adapter.delete_hotel(new_hotel)

        deleted_hotel = await hotel_adapter.get_hotel_by_id(hotel_id)
        assert deleted_hotel is None

    async def test_get_hotels_with_services_filter(self, hotel_adapter, manager):
        """Test filtering hotels by services."""
        hotel_with_wifi = Hotel(
            name="WiFi Hotel",
            location="Test Location",
            rooms_quantity=10,
            owner=manager.id,
            services={"wifi": True, "pool": False},
        )
        await hotel_adapter.add(hotel_with_wifi)

        hotels = await hotel_adapter.get_hotels(services={"wifi": True})

        assert len(hotels) >= 1
        assert all("wifi" in h.services for h in hotels if h.services)

    async def test_get_hotels_with_rooms_quantity_filter(self, hotel_adapter, manager):
        """Test filtering hotels by minimum rooms quantity."""
        hotels = await hotel_adapter.get_hotels(rooms_quantity=5)

        assert all(h.rooms_quantity >= 5 for h in hotels)
