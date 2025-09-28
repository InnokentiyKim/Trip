from datetime import date, datetime, UTC
from decimal import Decimal
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, TIMESTAMP, Computed, DECIMAL, DATETIME
from src.common.domain.models import Base
import uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date_from: Mapped[date] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    date_to: Mapped[date] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    status: Mapped[BookingStatusEnum] = mapped_column(
        SAEnum(BookingStatusEnum, name="status", validate_strings=True),
        nullable=False, default=BookingStatusEnum.PENDING
    )
    price: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(DECIMAL, Computed("price * (date_to - date_from)"))
    total_days: Mapped[int] = mapped_column(Integer, Computed("date_to - date_from"))
    created_at: Mapped[datetime] = mapped_column(DATETIME(timezone=False), nullable=False, default=datetime.now(UTC))
    updated_at: Mapped[date] = mapped_column(DATETIME(timezone=False), nullable=False, default=datetime.now(UTC))

    user = relationship("User", back_populates="bookings", lazy="joined")
    room = relationship("Room", back_populates="bookings", lazy="joined")
