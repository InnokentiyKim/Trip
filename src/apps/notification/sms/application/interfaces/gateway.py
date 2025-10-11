from typing import Protocol

from src.apps.notification.sms.domain.model import SMSType


class SMSGatewayProto(Protocol):
    async def send_sms(self, sms_data: SMSType) -> None:
        """Send an SMS."""
        ...
