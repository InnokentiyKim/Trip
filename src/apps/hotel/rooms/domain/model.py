from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, JSON, ForeignKey, DECIMAL, Float

from apps.hotel.bookings.domain.model import Booking
from apps.hotel.hotels.domain.model import Hotel
from src.common.domain.models import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    services: Mapped[dict] = mapped_column(JSON, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    image_id: Mapped[int] = mapped_column(Integer, nullable=True)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="rooms", lazy="joined")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="room", lazy="selectin", uselist=True, cascade="all, delete-orphan"
    )

    def from_dict(self, data: dict) -> "Room":
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        return self
