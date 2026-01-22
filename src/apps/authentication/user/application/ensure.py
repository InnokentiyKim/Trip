from uuid import UUID

from src.apps.authentication.user.application import exceptions
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.domain.models import User
from src.common.application.ensure import ServiceEnsuranceBase


class UserServiceEnsurance(ServiceEnsuranceBase):
    """User service ensuring."""

    def __init__(self, gateway: UserGatewayProto) -> None:
        self._user = gateway

    async def user_exists(self, user_id: UUID) -> User:
        """Ensure that a user exists by its ID."""
        user = await self._user.get_user_by_id(user_id)
        if user is None:
            raise exceptions.UserNotFoundError
        return user

    async def user_with_email_exists(self, email: str) -> User:
        """Ensure that a user exists by its email."""
        user = await self._user.get_user_by_email(email)
        if user is None:
            raise exceptions.UserNotFoundError
        return user
