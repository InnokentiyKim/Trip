import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, DECIMAL, Enum as SAEnum
from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.apps.billing.bill.domain.enums import CurrencyEnum, BillingStatusEnum
from src.common.domain.models import Base


class BillingBase(MappedAsDataclass, Base):
    """Base class for billing ORM models."""
    __abstract__ = True


class Bill(BillingBase):
    __tablename__ = "bills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    currency: Mapped[CurrencyEnum] = mapped_column(
        SAEnum(CurrencyEnum, name="currency", validate_strings=True),
        nullable=False,
        default=CurrencyEnum.RUB,
    )
    status: Mapped[BillingStatusEnum] = mapped_column(
        SAEnum(BillingStatusEnum, name="status", validate_strings=True),
        nullable=False,
        default=BillingStatusEnum.PENDING,
    )

    @property
    def total_cost(self) -> Decimal:
        return self.total_days * self.price

    @property
    def is_pending(self) -> bool:
        return self.status == BillingStatusEnum.PENDING

    @property
    def is_paid(self) -> bool:
        return self.status == BillingStatusEnum.PAID

    @property
    def is_cancelled(self) -> bool:
        return self.status == BillingStatusEnum.CANCELED

    @property
    def is_failed(self) -> bool:
        return self.status == BillingStatusEnum.FAILED

    @property
    def is_refunded(self) -> bool:
        return self.status == BillingStatusEnum.REFUNDED

    @property
    def can_be_paid(self) -> bool:
        return self.status  == BillingStatusEnum.PENDING

    @property
    def can_be_cancelled(self) -> bool:
        return self.status == BillingStatusEnum.PENDING

    @property
    def can_be_refunded(self) -> bool:
        return self.status == BillingStatusEnum.PAID
