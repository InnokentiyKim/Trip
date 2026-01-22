from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.apps.notification.email.application.interfaces.gateway import EmailGatewayProto
from src.apps.notification.email.domain.model import EmailType
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class SMTPAdapter(EmailGatewayProto):
    def __init__(self, config: Configs, logger: CustomLoggerProto) -> None:
        smtp_configs = ConnectionConfig(
            MAIL_USERNAME=config.smtp_email.smtp_username,
            MAIL_PASSWORD=config.smtp_email.smtp_password,
            USE_CREDENTIALS=config.smtp_email.smtp_use_credentials,
            MAIL_FROM=config.smtp_email.mail_from,
            MAIL_FROM_NAME=config.smtp_email.mail_from_name,
            MAIL_SERVER=config.smtp_email.smtp_server,
            MAIL_PORT=config.smtp_email.smtp_port,
            MAIL_SSL_TLS=config.smtp_email.smtp_ssl_tls,
            MAIL_STARTTLS=config.smtp_email.smtp_starttls,
        )
        self._config = config
        self._logger = logger
        self.fastmail = FastMail(smtp_configs)

    async def send_email(self, email_data: EmailType) -> None:
        """
        Send an email using SMTP.

        Args:
            email_data (EmailType): The email details including recipients, subject, and template information.
        """
        self._logger.info(
            "SMTP: Sending email",
            subject=email_data.subject,
            recipients=email_data.recipients,
        )

        message = MessageSchema(
            subject=email_data.subject,
            recipients=email_data.recipients,
            body=email_data.rendered_content,  # type: ignore[union-attr]
            subtype=MessageType.html,
        )

        await self.fastmail.send_message(message)
        self._logger.info(
            "SMTP: Email sent successfully",
            subject=email_data.subject,
            recipients=email_data.recipients,
        )


class FakeEmailAdapter(EmailGatewayProto):
    def __init__(
        self,
        config: Configs,
        logger: CustomLoggerProto,
    ) -> None:
        self._config = config
        self._logger = logger

    async def send_email(self, email_details: EmailType) -> None:
        """
        Send an email using SMTP.

        Args:
            email_details (EmailType): The email details including recipients, subject, and template information.
        """
        self._logger.info(
            "SMTP: Sending email",
            subject=email_details.subject,
            recipients=email_details.recipients,
        )
        # Validate schema
        MessageSchema(
            subject=email_details.subject,
            recipients=email_details.recipients,
            body=email_details.rendered_content,
            subtype=MessageType.html,
        )
        self._logger.info(
            "SMTP: Email sent successfully",
            subject=email_details.subject,
            recipients=email_details.recipients,
        )
