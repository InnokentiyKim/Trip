from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.authentication.session.adapters.adapter import AuthSessionAdapter, PasswordResetTokenAdapter, \
    OTPCodeAdapter
from src.apps.authentication.session.application.ensure import AuthenticationServiceEnsurance
from src.apps.authentication.session.application.interfaces.gateway import (
    AuthSessionGatewayProto, PasswordResetTokenGatewayProto, OTPCodeGatewayProto
)
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

    @provide(provides=PasswordResetTokenGatewayProto)
    def provide_password_reset_token_adapter(self, session: AsyncSession) -> PasswordResetTokenGatewayProto:
        return PasswordResetTokenAdapter(session)

    @provide(provides=OTPCodeGatewayProto)
    def provide_otp_code_adapter(self, session: AsyncSession) -> OTPCodeGatewayProto:
        return OTPCodeAdapter(session)


def get_authentication_providers() -> list[Provider]:
    return [
        AuthenticationServiceProviders(),
        AuthenticationGatewayProviders()
    ]
