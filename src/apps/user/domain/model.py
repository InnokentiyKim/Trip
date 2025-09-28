from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean

from src.apps.hotel.bookings.domain.model import Booking
from src.common.domain.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    hotel = relationship("Hotel", back_populates="user", lazy="joined")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="user", lazy="joined", uselist=True, cascade="all, delete-orphan"
    )
