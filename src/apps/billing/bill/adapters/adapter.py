from uuid import UUID

from sqlalchemy import select

from src.apps.billing.bill.application.interfaces.gateway import BillGatewayProto
from src.apps.billing.bill.domain.enums import BillStatusEnum
from src.apps.billing.bill.domain.models import Bill
from src.common.adapters.adapter import SQLAlchemyGateway


class BillAdapter(SQLAlchemyGateway, BillGatewayProto):
    async def add(self, bill: Bill) -> None:
        """Add a new bill."""
        self.session.add(bill)
        await self.session.commit()

    async def get_bill_by_id(self, bill_id: UUID) -> Bill | None:
        """Retrieve a bill by its ID."""
        return await self.get_item_by_id(Bill, bill_id)

    async def get_bills_by_user_id(self, user_id: UUID) -> list[Bill]:
        """Retrieve all bills for a specific user."""
        result = await self.session.execute(
            select(Bill).where(Bill.user_id == user_id)
        )
        return list(result.scalars())

    async def get_bill_by_booking_id(self, booking_id: UUID) -> Bill | None:
        """Retrieve a bill by its booking ID."""
        return await self.get_one_item(Bill, booking_id=booking_id)

    async def update_bill_status(self, bill: Bill, status: BillStatusEnum) -> UUID | None:
        """Update the status of a bill."""
        bill.status = status
        await self.session.commit()
        return bill.id

