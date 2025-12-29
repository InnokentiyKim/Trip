import uuid
from decimal import Decimal

from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship
from sqlalchemy import Integer, String, JSON, ForeignKey, DECIMAL, UUID

from src.common.domain.models import Base
from src.apps.hotel.bookings.domain.models import Booking  # noqa: F401
from src.apps.hotel.hotels.domain.models import Hotel  # noqa: F401


class RoomBase(MappedAsDataclass, Base):
    """Base class for room ORM models."""
    __abstract__ = True


class Room(RoomBase):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False
    )
    owner: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    services: Mapped[dict] = mapped_column(JSON, nullable=True)
    image_id: Mapped[int] = mapped_column(Integer, nullable=True)

    hotel: Mapped["Hotel"] = relationship(
        "Hotel", back_populates="rooms", lazy="joined"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="room",
        lazy="selectin",
        uselist=True,
        cascade="all, delete-orphan",
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    def __init__(
        self,
        hotel_id: int,
        owner: uuid.UUID,
        name: str,
        price: Decimal,
        description: str | None,
        services: dict | None,
        image_id: int | None,
        quantity: int = 1,
    ) -> None:
        super().__init__()
        self.hotel_id = hotel_id
        self.owner = owner
        self.name = name
        self.description = description
        self.price = price
        self.services = services
        self.image_id = image_id
        self.quantity = quantity
