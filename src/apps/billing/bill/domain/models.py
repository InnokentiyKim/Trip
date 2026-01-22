import uuid
from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from src.apps.billing.bill.domain.enums import BillingStatusEnum, CurrencyEnum
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
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
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
        """Calculate the total cost of the bill."""
        return self.total_days * self.price

    @property
    def is_pending(self) -> bool:
        """Check if the bill is in pending status."""
        return self.status == BillingStatusEnum.PENDING

    @property
    def is_paid(self) -> bool:
        """Check if the bill is in paid status."""
        return self.status == BillingStatusEnum.PAID

    @property
    def is_cancelled(self) -> bool:
        """Check if the bill is in canceled status."""
        return self.status == BillingStatusEnum.CANCELED

    @property
    def is_failed(self) -> bool:
        """Check if the bill is in failed status."""
        return self.status == BillingStatusEnum.FAILED

    @property
    def is_refunded(self) -> bool:
        """Check if the bill is in refunded status."""
        return self.status == BillingStatusEnum.REFUNDED

    @property
    def can_be_paid(self) -> bool:
        """Check if the bill can be paid."""
        return self.status == BillingStatusEnum.PENDING

    @property
    def can_be_cancelled(self) -> bool:
        """Check if the bill can be cancelled."""
        return self.status == BillingStatusEnum.PENDING

    @property
    def can_be_refunded(self) -> bool:
        """Check if the bill can be refunded."""
        return self.status == BillingStatusEnum.PAID
