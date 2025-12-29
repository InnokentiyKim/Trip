from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.authorization.access.adapters.adapter import AccessAdapter
from src.apps.authorization.access.application.interfaces.gateway import AccessGatewayProto
from src.apps.authorization.access.application.service import AccessService
from src.apps.authorization.role.adapters.adapter import RoleAdapter, PermissionsAdapter
from src.apps.authorization.role.application.ensure import RoleServiceEnsurance
from src.apps.authorization.role.application.interfaces.gateway import RoleGatewayProto, PermissionGatewayProto
from src.apps.authorization.role.application.service import RoleManagementService


class AuthorizationServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        AccessService,
        RoleManagementService,
        RoleServiceEnsurance,
    )


class AuthorizationGatewayProviders(Provider):
    scope = Scope.REQUEST

    @provide(provides=RoleGatewayProto)
    def provide_role_adapter(self, session: AsyncSession) -> RoleGatewayProto:
        return RoleAdapter(session)

    @provide(provides=AccessGatewayProto)
    def provide_access_adapter(self, session: AsyncSession) -> AccessGatewayProto:
        return AccessAdapter(session)

    @provide(provides=PermissionGatewayProto)
    def provide_permission_adapter(self, session: AsyncSession) -> PermissionGatewayProto:
        return PermissionsAdapter(session)


def get_authorization_providers() -> list[Provider]:
    return [
        AuthorizationServiceProviders(),
        AuthorizationGatewayProviders()
    ]
