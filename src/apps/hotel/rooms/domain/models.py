import uuid
from decimal import Decimal

from sqlalchemy import DECIMAL, UUID, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.hotels.domain.models import Hotel
from src.common.domain.models import Base


class RoomBase(MappedAsDataclass, Base):
    """Base class for room ORM models."""

    __abstract__ = True


class Room(RoomBase):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("hotel_id", "name", name="unq_room_hotel_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False
    )
    owner: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    services: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    image_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="rooms",
        lazy="joined",
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
        hotel_id: uuid.UUID,
        owner: uuid.UUID,
        name: str,
        price: Decimal,
        description: str | None = None,
        services: dict | None = None,
        image_id: int | None = None,
        quantity: int = 1,
    ) -> None:
        super().__init__()
        self.id = uuid.uuid4()
        self.hotel_id = hotel_id
        self.owner = owner
        self.name = name
        self.description = description
        self.price = price
        self.services = services
        self.image_id = image_id
        self.quantity = quantity
