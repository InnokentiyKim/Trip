from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP, Computed, DECIMAL
from src.common.domain.models import Base
import uuid
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date_from: Mapped[date] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    date_to: Mapped[date] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(DECIMAL, Computed("price * (date_to - date_from)"))
    total_days: Mapped[int] = mapped_column(Integer, Computed("date_to - date_from"))
