from uuid import UUID

from src.apps.hotel.hotels.application.exceptions import HotelNotFoundException
from src.common.adapters.adapter import SQLAlchemyGateway
from src.common.utils.dependency import SessionDependency
from src.apps.hotel.hotels.domain.model import Hotel
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto


class HotelAdapter(SQLAlchemyGateway, HotelGatewayProto):
    async def get_hotels(self, **filters) -> list[Hotel]:
        """Retrieve a list of hotels."""
        hotels = await self.get_items_list(SessionDependency, Hotel, **filters)
        return hotels

    async def get_hotel_by_id(self, hotel_id: int) -> Hotel | None:
        """Retrieve a hotel by its ID."""
        hotel = self.get_item_by_id(SessionDependency, Hotel, hotel_id)
        return hotel

    async def create_hotel(self, name: str, location: str, services: dict, rooms_quantity: int, owner_id: int | UUID, image_id: int | None) -> None:
        """Add a new hotel."""
        new_hotel = Hotel(
            name=name,
            location=location,
            services=services,
            rooms_quantity=rooms_quantity,
            owner=owner_id,
            image_id=image_id
        )
        await self.add_item(SessionDependency, new_hotel)

    async def update_hotel(self, user_id: int, hotel_id: int, **params) -> int | None:
        """Update an existing hotel."""
        hotel = await self.get_one_item(SessionDependency, Hotel, id=hotel_id, owner_id=user_id)
        if not hotel:
            raise HotelNotFoundException
        for key, value in params.items():
            setattr(hotel, key, value)
        await self.add_item(SessionDependency, hotel)
        return hotel.id

    async def delete_hotel(self, user_id: int, hotel_id: int) -> int | None:
        """Delete a hotel by its ID."""
        hotel = await self.get_one_item(SessionDependency, Hotel, id=hotel_id, owner_id=user_id)
        if not hotel:
            raise HotelNotFoundException
        await self.delete_item(SessionDependency, hotel)
        return hotel_id
