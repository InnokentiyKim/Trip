import uuid

import pytest

from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.hotels.domain import commands
from src.apps.hotel.hotels.application import exceptions
from src.apps.hotel.hotels.domain.models import Hotel
from tests.fixtures.mocks import MockUser, MockHotel


@pytest.fixture
async def hotel_service(request_container) -> HotelService:
    """Create a hotel service for testing."""
    return await request_container.get(HotelService)


@pytest.fixture(autouse=True)
async def mock_data(save_instances, user, manager, hotel, existing_hotel) -> None:
    """Save required dependencies to database for tests with --no-fake."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, existing_hotel]))


@pytest.mark.asyncio
class TestHotelService:
    async def test_list_hotels(self, hotel_service):
        """Test listing all hotels."""
        cmd = commands.ListHotelsCommand(
            location=None,
            services=None,
            rooms_quantity=None,
        )
        hotels = await hotel_service.list_hotels(cmd)

        assert isinstance(hotels, list)
        assert len(hotels) >= 1
        assert all(isinstance(h, Hotel) for h in hotels)

    async def test_get_hotel_success(self, hotel_service, hotel):
        """Test getting an existing hotel."""
        cmd = commands.GetHotelCommand(hotel_id=hotel.id)
        result = await hotel_service.get_hotel(cmd)

        assert result.id == hotel.id
        assert result.name == hotel.name

    async def test_get_hotel_not_found(self, hotel_service):
        """Test getting a non-existent hotel."""
        cmd = commands.GetHotelCommand(hotel_id=uuid.uuid4())

        with pytest.raises(exceptions.HotelNotFoundException):
            await hotel_service.get_hotel(cmd)

    async def test_create_hotel_success(self, hotel_service, manager):
        """Test creating a new hotel."""
        manager_id = manager.id
        cmd = commands.CreateHotelCommand(
            name="Test_NEW_Hotel",
            location="Test_NEW_Location",
            rooms_quantity=50,
            owner=manager_id,
            services={"WiFi": True, "Parking": True},
            is_active=True,
            image_id=None,
        )

        new_hotel_id = await hotel_service.create_hotel(cmd)

        assert isinstance(new_hotel_id, uuid.UUID)

    async def test_create_hotel_already_exists(self, hotel_service, hotel):
        """Test creating a hotel that already exists."""
        cmd = commands.CreateHotelCommand(
            name=hotel.name,
            location=hotel.location,
            rooms_quantity=hotel.rooms_quantity,
            owner=hotel.owner,
            services=hotel.services or None,
            image_id=hotel.image_id,
            is_active=True,
        )

        with pytest.raises(exceptions.HotelAlreadyExistsException):
            await hotel_service.create_hotel(cmd)

    async def test_update_hotel_success(self, hotel_service, manager, hotel):
        """Test updating an existing hotel."""
        cmd = commands.UpdateHotelCommand(
            hotel_id=hotel.id,
            owner=manager.id,
            name="Updated Name",
            rooms_quantity=100,
            location=None,
            services=None,
            is_active=None,
            image_id=None,
        )

        updated_id = await hotel_service.update_hotel(cmd)

        assert updated_id == hotel.id

    async def test_update_hotel_cannot_be_updated(self, hotel_service, hotel, existing_hotel):
        """Test updating an existing hotel."""
        cmd = commands.UpdateHotelCommand(
            hotel_id=hotel.id,
            owner=hotel.owner,
            name=existing_hotel.name, # Existing name/location to trigger cannot be updated
            location=existing_hotel.location,
            rooms_quantity=None,
            services=None,
            is_active=None,
            image_id=None,
        )

        with pytest.raises(exceptions.HotelCannotBeUpdatedException):
            await hotel_service.update_hotel(cmd)

    async def test_update_hotel_not_found(self, hotel_service, manager):
        """Test updating a non-existent hotel."""
        hotel_id = uuid.uuid4()
        cmd = commands.UpdateHotelCommand(
            hotel_id=hotel_id,
            owner=manager.id,
            name="Updated Name",
            rooms_quantity=None,
            location=None,
            services=None,
            is_active=None,
            image_id=None,
        )

        with pytest.raises(exceptions.HotelNotFoundException):
            await hotel_service.update_hotel(cmd)

    async def test_delete_hotel_success(self, hotel_service, hotel):
        """Test deleting an existing hotel."""
        cmd = commands.DeleteHotelCommand(hotel_id=hotel.id)

        await hotel_service.delete_hotel(cmd)

        # Verify deletion
        with pytest.raises(exceptions.HotelNotFoundException):
            get_cmd = commands.GetHotelCommand(hotel_id=hotel.id)
            await hotel_service.get_hotel(get_cmd)

    async def test_delete_hotel_not_found(self, hotel_service):
        """Test deleting a non-existent hotel."""
        hotel_id = uuid.uuid4()
        cmd = commands.DeleteHotelCommand(hotel_id=hotel_id)

        with pytest.raises(exceptions.HotelNotFoundException):
            await hotel_service.delete_hotel(cmd)
