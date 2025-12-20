from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.authentication.user.adapters.adapter import UserAdapter
from src.apps.authentication.user.application.ensure import UserServiceInsurance
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.application.service import UserService


class UserServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        UserService,
        UserServiceInsurance,
    )


class UserGatewayProviders(Provider):
    scope = Scope.REQUEST

    @provide(provides=UserGatewayProto)
    def provide_user_adapter(self, session: AsyncSession) -> UserGatewayProto:
        return UserAdapter(session)


def get_user_providers() -> list[Provider]:
    return [UserServiceProviders(), UserGatewayProviders()]
