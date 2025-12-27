from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.authentication.session.adapters.adapter import AuthSessionAdapter
from src.apps.authentication.session.application.ensure import AuthenticationServiceEnsurance
from src.apps.authentication.session.application.interfaces.gateway import AuthSessionGatewayProto
from src.apps.authentication.session.application.service import AuthenticationService
from src.apps.authentication.user.adapters.adapter import UserAdapter
from src.apps.authentication.user.application.ensure import UserServiceEnsurance
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.application.service import UserService


class AuthenticationServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        UserService,
        UserServiceEnsurance,
        AuthenticationService,
        AuthenticationServiceEnsurance,
    )


class AuthenticationGatewayProviders(Provider):
    scope = Scope.REQUEST

    @provide(provides=UserGatewayProto)
    def provide_user_adapter(self, session: AsyncSession) -> UserGatewayProto:
        return UserAdapter(session)

    @provide(provides=AuthSessionGatewayProto)
    def provide_auth_session_adapter(self, session: AsyncSession) -> AuthSessionGatewayProto:
        return AuthSessionAdapter(session)


def get_user_providers() -> list[Provider]:
    return [
        AuthenticationServiceProviders(),
        AuthenticationGatewayProviders()
    ]
