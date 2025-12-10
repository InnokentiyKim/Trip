from datetime import date, datetime, UTC
from decimal import Decimal
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, TIMESTAMP, Computed, DECIMAL, Date
from src.common.domain.models import Base
import uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID


class BookingBase(MappedAsDataclass, Base):
    """Base class for booking ORM models."""
    __abstract__ = True


class Booking(BookingBase):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 4), Computed("price * (date_to - date_from)")
    )
    total_days: Mapped[int] = mapped_column(Integer, Computed("(date_to - date_from)"))

    user: Mapped["User"] = relationship("User", back_populates="bookings", lazy="joined")
    room: Mapped["Room"] = relationship("Room", back_populates="bookings", lazy="joined")

    status: Mapped[BookingStatusEnum] = mapped_column(
        SAEnum(BookingStatusEnum, name="status", validate_strings=True),
        nullable=False,
        default=BookingStatusEnum.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, default=datetime.now(UTC)
    )
    updated_at: Mapped[date] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, default=datetime.now(UTC)
    )
