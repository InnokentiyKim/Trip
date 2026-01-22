import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, TIMESTAMP, Computed, Date, ForeignKey, Index, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from src.apps.authentication.user.domain.models import User
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.common.domain.models import Base

if TYPE_CHECKING:
    from src.apps.hotel.rooms.domain.models import Room


class BookingBase(MappedAsDataclass, Base):
    """Base class for booking ORM models."""

    __abstract__ = True


class Booking(BookingBase):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, Computed("(date_to - date_from)"))

    user: Mapped["User"] = relationship("User", back_populates="bookings", lazy="joined")
    room: Mapped["Room"] = relationship("Room", back_populates="bookings", lazy="joined")

    status: Mapped[BookingStatusEnum] = mapped_column(
        SAEnum(BookingStatusEnum, name="status", validate_strings=True),
        nullable=False,
        default=BookingStatusEnum.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(UTC))
    updated_at: Mapped[date] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(UTC))

    __table_args__ = (Index("ix_booking_updated_at_room_id", "updated_at", "room_id"),)

    def __init__(
        self,
        room_id: uuid.UUID,
        user_id: uuid.UUID,
        date_from: date,
        date_to: date,
        price: Decimal,
        status: BookingStatusEnum = BookingStatusEnum.PENDING,
    ) -> None:
        super().__init__()
        self.id = uuid.uuid4()
        self.room_id = room_id
        self.user_id = user_id
        self.date_from = date_from
        self.date_to = date_to
        self.price = price
        self.status = status
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now

    @property
    def total_cost(self) -> Decimal:
        """Calculate the total cost of the booking."""
        return self.price * Decimal(self.total_days)
