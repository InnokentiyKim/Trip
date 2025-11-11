from sqlalchemy.exc import IntegrityError
from src.common.adapters.adapter import SQLAlchemyGateway
from src.common.utils.dependency import SessionDependency
from src.apps.hotel.hotels.domain.model import Hotel
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from sqlalchemy import select


class HotelAdapter(SQLAlchemyGateway, HotelGatewayProto):
    async def get_hotels(self, only_active: bool = True, **filters) -> list[Hotel]:
        """Retrieve a list of hotels."""
        location = filters.get('location', None)
        services = filters.get('services', None)
        rooms_quantity = filters.get('rooms_quantity', None)
        criteria = []
        if only_active:
            criteria.append(Hotel.is_active.is_(True))
        if location:
            criteria.append(Hotel.location == location)
        if services:
            criteria.append(Hotel.services.contains(services))
        if rooms_quantity:
            criteria.append(Hotel.rooms_quantity >= rooms_quantity)
        stmt = select(Hotel).where(**criteria)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_hotel_by_id(self, hotel_id: int) -> Hotel | None:
        """Retrieve a hotel by its ID."""
        hotel = self.get_item_by_id(SessionDependency, Hotel, hotel_id)
        return hotel

    async def add_hotel(self, hotel: Hotel) -> int | None:
        """Add a new hotel."""
        self.session.add(hotel)
        try:
            await self.session.commit()
            return hotel.id
        except IntegrityError:
            return None

    async def update_hotel(self, hotel: Hotel, **params) -> int | None:
        """Update an existing hotel."""
        hotel = await self.get_one_item(SessionDependency, Hotel, id=hotel_id, owner_id=user_id)
        if not hotel:
            return None
        for key, value in params.items():
            setattr(hotel, key, value)
        await self.add_item(SessionDependency, hotel)
        return hotel.id

    async def delete_hotel(self, hotel: Hotel) -> None:
        """Delete a hotel by its ID."""
        await self.delete_item(SessionDependency, hotel)
