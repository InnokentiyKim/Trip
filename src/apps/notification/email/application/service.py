from src.apps.notification.email.application.interfaces.gateway import EmailGatewayProto
from src.apps.notification.email.domain import model as email_model
from src.apps.notification.email.domain.commands import SendBookingConfirmationEmail
from src.common.application.service import ServiceBase
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class EmailService(ServiceBase):
    def __init__(self, email: EmailGatewayProto, logger: CustomLoggerProto, config: Configs) -> None:
        self._email = email
        self._logger = logger
        self._config = config.smtp_email
        super().__init__()

    async def send_booking_confirmation_email(self, cmd: SendBookingConfirmationEmail) -> None:
        """Send booking confirmation email."""
        confirmation_email = email_model.ConfirmationEmail(
            subject=cmd.subject,
            recipients=[cmd.email],
            from_email=self._config.mail_from,
            template_name=cmd.template_name,
        )
        await self._email.send_email(confirmation_email)
        self._logger.info("Booking confirmation email sent", email_to=cmd.email)
