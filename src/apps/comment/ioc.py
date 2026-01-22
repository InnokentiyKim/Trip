from dishka import AsyncContainer, Provider, Scope, provide

from src.apps.comment.adapters.adapter import CommentAdapter
from src.apps.comment.application.interfaces.gateway import CommentGatewayProto
from src.apps.comment.application.service import CommentService
from src.common.domain.enums import GatewayTypeEnum


class CommentServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide(
        CommentService,
    )


class CommentGatewayProviders(Provider):
    """Provides comment gateway implementations."""

    scope = Scope.REQUEST

    _alchemy_comment_gateway = provide(CommentAdapter)

    @provide(provides=CommentGatewayProto)
    async def provide_comment_gateway(self, request_container: AsyncContainer) -> CommentGatewayProto:
        """Provides a CommentGatewayProto implementation based on the configured gateway type."""
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(CommentAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")


def get_comment_providers() -> list[Provider]:
    """Get the list of comment service and gateway providers."""
    return [CommentServiceProviders(), CommentGatewayProviders()]
