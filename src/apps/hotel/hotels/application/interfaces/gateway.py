from abc import abstractmethod
from uuid import UUID

from src.apps.hotel.hotels.domain.models import Hotel
from src.common.interfaces import GatewayProto


class HotelGatewayProto(GatewayProto):
    @abstractmethod
    async def get_hotels(self, only_active: bool = True, **filters) -> list[Hotel]:
        """Retrieve a list of hotels."""
        ...

    @abstractmethod
    async def get_hotel_by_id(self, hotel_id: int) -> Hotel | None:
        """Retrieve a hotel by its ID."""
        ...

    @abstractmethod
    async def get_users_hotel(self, user_id: UUID, hotel_id: int) -> Hotel | None:
        """Retrieve users hotel by its ID."""
        ...

    @abstractmethod
    async def add_hotel(self, hotel: Hotel) -> int | None:
        """Add a new hotel."""
        ...

    @abstractmethod
    async def update_hotel(self, hotel: Hotel, **params) -> int | None:
        """Update an existing hotel."""
        ...

    @abstractmethod
    async def delete_hotel(self, hotel: Hotel) -> None:
        """Delete a hotel by its ID."""
        ...
