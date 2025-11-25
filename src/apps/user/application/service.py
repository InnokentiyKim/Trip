from src.infrastructure.security.application.exceptions import InvalidTokenException
from src.apps.user.application.exceptions import UserAlreadyExistsException
from src.infrastructure.security.adapters.adapter import SecurityAdapter
from src.apps.user.adapters.adapter import UserAdapter
from src.common.application.service import ServiceBase
from src.apps.user.domain.models import User
from src.apps.user.application.ensure import UserServiceInsurance
from src.apps.user.domain import commands


class UserService(ServiceBase):
    def __init__(
        self,
        user_adapter: UserAdapter,
        auth_adapter: SecurityAdapter,
        user_ensure: UserServiceInsurance,
    ) -> None:
        self._user = user_adapter
        self._auth = auth_adapter
        self._user_ensure = user_ensure

    async def register_user(self, cmd: commands.CreateUserCommand) -> User:
        user = await self._user_ensure.user_with_email_exists(cmd.email)
        if user:
            raise UserAlreadyExistsException
        hashed_password = self._auth.get_password_hash(cmd.password)
        new_user = User(
            email=cmd.email,
            hashed_password=hashed_password,
            name=cmd.name,
            phone=cmd.phone,
            avatar_url=cmd.avatar_url,
            is_active=cmd.is_active,
        )
        await self._user.add_user(new_user)
        return new_user

    async def login_user(self, cmd: commands.LoginUserCommand) -> str:
        user = await self._user_ensure.user_with_email_exists(cmd.email)
        if not self._auth.verify_password(cmd.password, user.hashed_password):
            raise InvalidTokenException
        access_token = self._auth.create_access_token(data={"sub": str(user.id)})
        return access_token

    async def verify_user_by_token(
        self, cmd: commands.VerifyUserByTokenCommand
    ) -> User:
        user_id = self._auth.verify_access_token(cmd.token)
        user = await self._user_ensure.user_exists(user_id)

        return user
