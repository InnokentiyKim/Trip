from sqlalchemy.exc import IntegrityError
from src.common.adapters.adapter import SQLAlchemyGateway
from src.apps.hotel.hotels.domain.models import Hotel
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
            criteria.append(Hotel.location==location)
        if services:
            criteria.append(Hotel.services.contains(services))
        if rooms_quantity:
            criteria.append(Hotel.rooms_quantity>=rooms_quantity)
        stmt = select(Hotel).where(**criteria)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def get_hotel_by_id(self, hotel_id: int) -> Hotel | None:
        """Retrieve a hotel by its ID."""
        hotel = await self.get_item_by_id(Hotel, hotel_id)
        return hotel

    async def add_hotel(self, hotel: Hotel) -> int | None:
        """Add a new hotel."""
        self._session.add(hotel)
        try:
            await self._session.commit()
            return hotel.id
        except IntegrityError:
            return None

    async def update_hotel(self, hotel: Hotel, **params) -> int | None:
        """Update an existing hotel."""
        for key, value in params.items():
            setattr(hotel, key, value)
        await self.add_item(hotel)
        return hotel.id

    async def delete_hotel(self, hotel: Hotel) -> None:
        """Delete a hotel by its ID."""
        await self.delete_item(hotel)
