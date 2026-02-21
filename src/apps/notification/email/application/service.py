from src.apps.notification.email.application.interfaces.gateway import EmailGatewayProto
from src.apps.notification.email.domain import model as email_model
from src.apps.notification.email.domain.commands import SendBookingConfirmationEmail, SendWelcomeEmail
from src.common.application.service import ServiceBase
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class EmailService(ServiceBase):
    def __init__(self, email: EmailGatewayProto, logger: CustomLoggerProto, config: Configs) -> None:
        self._email = email
        self._logger = logger
        self._config = config
        super().__init__()

    async def send_welcome_email(self, cmd: SendWelcomeEmail) -> None:
        """Send welcome email."""
        welcome_email = email_model.UserSingUpEmail(
            template_name=cmd.template_name,
            subject=cmd.subject,
            recipients=[cmd.email],
            from_email=self._config.smtp_email.mail_from,
            call_to_action_link=self._config.general.website_url,
        )

        await self._email.send_email(welcome_email)
        self._logger.info("Welcome email sent", email_to=cmd.email)

    async def send_booking_confirmation_email(self, cmd: SendBookingConfirmationEmail) -> None:
        """Send booking confirmation email."""
        confirmation_email = email_model.ConfirmationEmail(
            template_name=cmd.template_name,
            subject=cmd.subject,
            recipients=[cmd.email],
            from_email=self._config.smtp_email.mail_from,
            additional_data={
                "hotel_name": cmd.hotel_name,
                "room_numbers": ", ".join(cmd.room_numbers),
                "date_from": cmd.date_from.strftime("%Y-%m-%d"),
                "date_to": cmd.date_to.strftime("%Y-%m-%d"),
                "total_price": str(cmd.total_price),
            },
        )

        await self._email.send_email(confirmation_email)
        self._logger.info("Booking confirmation email sent", email_to=cmd.email)
