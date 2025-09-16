from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, JSON, ForeignKey, DECIMAL, Float
from src.common.domain.models import Base


class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    services: Mapped[dict] = mapped_column(JSON, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    image_id: Mapped[int] = mapped_column(Integer, nullable=True)
