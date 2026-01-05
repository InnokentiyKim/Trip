from uuid import UUID

from sqlalchemy.exc import IntegrityError
from src.common.adapters.adapter import SQLAlchemyGateway, FakeGateway
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.hotels.application.interfaces.gateway import HotelGatewayProto
from sqlalchemy import select


class HotelAdapter(SQLAlchemyGateway, HotelGatewayProto):
    async def get_hotels(self, only_active: bool = True, **filters) -> list[Hotel]:
        """Retrieve a list of hotels."""
        location = filters.get("location", None)
        services = filters.get("services", None)
        rooms_quantity = filters.get("rooms_quantity", None)
        criteria = []
        if only_active:
            criteria.append(Hotel.is_active.is_(True))
        if location:
            criteria.append(Hotel.location == location)
        if services:
            criteria.append(Hotel.services.contains(services))
        if rooms_quantity:
            criteria.append(Hotel.rooms_quantity >= rooms_quantity)
        stmt = select(Hotel).filter(*criteria)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_hotel_by_id(self, hotel_id: UUID) -> Hotel | None:
        """Retrieve a hotel by its ID."""
        hotel = await self.get_item_by_id(Hotel, hotel_id)
        return hotel

    async def get_users_hotel(self, user_id: UUID, hotel_id: UUID) -> Hotel | None:
        """Retrieve users hotel by its ID."""
        hotel = await self.get_one_item(Hotel, id=hotel_id, owner_id=user_id)
        return hotel

    async def add(self, hotel: Hotel) -> UUID | None:
        """Add a new hotel."""
        self.session.add(hotel)
        try:
            await self.session.commit()
            return hotel.id
        except IntegrityError:
            return None

    async def update_hotel(self, hotel: Hotel, **params) -> UUID | None:
        """Update an existing hotel."""
        for key, value in params.items():
            setattr(hotel, key, value)
        await self.add(hotel)
        return hotel.id

    async def delete_hotel(self, hotel: Hotel) -> None:
        """Delete a hotel by its ID."""
        await self.delete_item(hotel)


class FakeHotelAdapter(FakeGateway[Hotel], HotelGatewayProto):
    async def get_hotels(self, only_active: bool = True, **filters) -> list[Hotel]:
        """Retrieve a list of hotels."""
        if only_active:
            return [
                hotel
                for hotel in self._collection
                if hotel.is_active and all(getattr(hotel, k) == v for k, v in filters.items())
            ]

        return [
            hotel
            for hotel in self._collection
            if all(getattr(hotel, k) == v for k, v in filters.items())
        ]


    async def get_hotel_by_id(self, hotel_id: UUID) -> Hotel | None:
        """Retrieve a hotel by its ID."""
        return next((hotel for hotel in self._collection if hotel.id == hotel_id), None)

    async def get_users_hotel(self, user_id: UUID, hotel_id: UUID) -> Hotel | None:
        """Retrieve users hotel by its ID."""
        return next(hotel for hotel in self._collection if hotel.id == hotel_id and hotel.owner == user_id)

    async def add(self, hotel: Hotel) -> UUID | None:
        """Add a new hotel."""
        self._collection.add(hotel)

    async def update_hotel(self, hotel: Hotel, **params) -> UUID | None:
        """Update an existing hotel."""
        for key, value in params.items():
            setattr(hotel, key, value)

        self._collection.discard(hotel)
        self._collection.add(hotel)

        return hotel.id

    async def delete_hotel(self, hotel: Hotel) -> None:
        """Delete a hotel by its ID."""
        self._collection.discard(hotel)
