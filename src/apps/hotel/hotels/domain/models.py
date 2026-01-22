import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from src.common.domain.models import Base

if TYPE_CHECKING:
    from src.apps.authentication.user.domain.models import User
    from src.apps.hotel.rooms.domain.models import Room


class HotelBase(MappedAsDataclass, Base):
    """Base class for hotel ORM models."""

    __abstract__ = True


class Hotel(HotelBase):
    __tablename__ = "hotels"
    __table_args__ = (UniqueConstraint("name", "location", name="unq_hotel_name_location"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    services: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    rooms_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    owner: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    image_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="hotel", lazy="joined")
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="hotel",
        lazy="selectin",
        uselist=True,
        cascade="all, delete-orphan",
    )

    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    def __init__(
        self,
        name: str,
        location: str,
        services: dict | None,
        rooms_quantity: int,
        owner: uuid.UUID,
        is_active: bool = True,
        image_id: int | None = None,
    ) -> None:
        super().__init__()
        self.id = uuid.uuid4()
        self.name = name
        self.location = location
        self.services = services if services else {}
        self.rooms_quantity = rooms_quantity
        self.owner = owner
        self.is_active = is_active
        self.image_id = image_id
