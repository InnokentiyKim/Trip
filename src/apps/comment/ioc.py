from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.comment.adapters.adapter import CommentAdapter
from src.apps.comment.application.interfaces.gateway import CommentGatewayProto
from src.apps.comment.application.service import CommentService


class CommentServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide(
        CommentService,
    )


class CommentGatewayProviders(Provider):
    scope = Scope.REQUEST

    @provide(provides=CommentGatewayProto)
    def provide_role_adapter(self, session: AsyncSession) -> CommentGatewayProto:
        return CommentAdapter(session)


def get_comment_providers() -> list[Provider]:
    return [
        CommentServiceProviders(),
        CommentGatewayProviders()
    ]
