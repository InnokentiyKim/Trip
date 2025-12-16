from dishka import Provider, provide, provide_all, Scope

from src.apps.notification.email.adapters.smtp import SMTPAdapter
from src.apps.notification.email.application.interfaces.gateway import EmailGatewayProto
from src.apps.notification.email.application.service import EmailService
from src.apps.notification.sms.application.service import SMSService
from src.config import Configs


class ServiceProviders(Provider):
    scope = Scope.REQUEST

    notification_services = provide_all(
        EmailService,
        SMSService,
    )


class GatewayProviders(Provider):
    scope = Scope.APP

    @provide(provides=EmailGatewayProto)
    async def provide_email_adapter(self, config: Configs):
        return SMTPAdapter(config)


def get_notification_providers() -> list[Provider]:
    return [ServiceProviders(), GatewayProviders()]
