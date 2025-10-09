from abc import abstractmethod
from typing import Protocol
from src.apps.notification.email.domain.model import EmailType


class EmailGatewayProto(Protocol):
    @abstractmethod
    async def send_email(self, email_data: EmailType) -> None:
        """Send an email."""
        ...
