from src.apps.user.application.interfaces.gateway import UserGatewayProto
from src.apps.user.domain.models import User
from src.common.application.ensure import ServiceInsuranceBase
from src.apps.user.application import exceptions


class UserServiceInsurance(ServiceInsuranceBase):
    """User service ensuring."""
    def __init__(
        self,
        gateway: UserGatewayProto
    ) -> None:
        self._user = gateway

    async def user_exists(self, user_id: int) -> User:
        user = await self._user.get_user_by_id(user_id)
        if user is None:
            raise exceptions.UserNotFoundException
        return user

    async def user_with_email_exists(self, email: str) -> User:
        user = await self._user.get_user_by_email(email)
        if user is None:
            raise exceptions.UserNotFoundException
        return user
