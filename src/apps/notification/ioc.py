from dishka import Provider, Scope, provide, provide_all

from src.apps.notification.email.adapters.smtp import SMTPAdapter
from src.apps.notification.email.application.interfaces.gateway import EmailGatewayProto
from src.apps.notification.email.application.service import EmailService
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class ServiceProviders(Provider):
    scope = Scope.REQUEST

    notification_services = provide_all(
        EmailService,
        # SMSService,
    )


class GatewayProviders(Provider):
    """Provides notification gateway implementations."""

    scope = Scope.APP

    @provide(provides=EmailGatewayProto)
    async def provide_email_adapter(self, config: Configs, logger: CustomLoggerProto) -> EmailGatewayProto:
        """Provides an SMTPAdapter instance configured with application settings."""
        return SMTPAdapter(config, logger)


def get_notification_providers() -> list[Provider]:
    """Get the list of notification service and gateway providers."""
    return [ServiceProviders(), GatewayProviders()]
