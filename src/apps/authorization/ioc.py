from dishka import AsyncContainer, Provider, Scope, provide, provide_all

from src.apps.authorization.access.adapters.adapter import AccessAdapter
from src.apps.authorization.access.application.interfaces.gateway import (
    AccessGatewayProto,
)
from src.apps.authorization.access.application.service import AccessService
from src.apps.authorization.role.adapters.adapter import PermissionsAdapter, RoleAdapter
from src.apps.authorization.role.application.ensure import RoleServiceEnsurance
from src.apps.authorization.role.application.interfaces.gateway import (
    PermissionGatewayProto,
    RoleGatewayProto,
)
from src.apps.authorization.role.application.service import RoleManagementService
from src.common.domain.enums import GatewayTypeEnum


class AuthorizationServiceProviders(Provider):
    """Register authorization service providers."""

    scope = Scope.REQUEST

    services = provide_all(
        AccessService,
        RoleManagementService,
        RoleServiceEnsurance,
    )


class AuthorizationGatewayProviders(Provider):
    """Register authorization gateway providers."""

    scope = Scope.REQUEST

    _alchemy_role_gateway = provide(RoleAdapter)
    _alchemy_access_gateway = provide(AccessAdapter)
    _alchemy_permission_gateway = provide(PermissionsAdapter)

    @provide(provides=RoleGatewayProto)
    async def provide_role_gateway(self, request_container: AsyncContainer) -> RoleGatewayProto:
        """Provides a RoleGatewayProto implementation based on the configured gateway type."""
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(RoleAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")

    @provide(provides=AccessGatewayProto)
    async def provide_access_gateway(self, request_container: AsyncContainer) -> AccessGatewayProto:
        """Provides an AccessGatewayProto implementation based on the configured gateway type."""
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(AccessAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")

    @provide(provides=PermissionGatewayProto)
    async def provide_permission_gateway(self, request_container: AsyncContainer) -> PermissionGatewayProto:
        """
        Provides a PermissionGatewayProto implementation based on the configured gateway type.

        Args:
            request_container: Dependency injection container.

        Returns:
            PermissionGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(PermissionsAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")


def get_authorization_providers() -> list[Provider]:
    """Get the list of authorization service and gateway providers."""
    return [AuthorizationServiceProviders(), AuthorizationGatewayProviders()]
