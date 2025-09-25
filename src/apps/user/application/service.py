from pydantic import EmailStr

from apps.security.application.exceptions import TokenIsMissingException
from src.apps.security.application.exceptions import InvalidTokenException
from apps.user.application.exceptions import UserAlreadyExistsException, UserNotFoundException
from src.config import Configs
from src.apps.security.adapters.adapter import SecurityAdapter
from src.apps.user.adapters.adapter import UserAdapter
from common.application.service import ServiceBase
from src.apps.user.domain.model import Users


config = Configs()

class UserService(ServiceBase):
    def __init__(
        self,
        user_adapter: UserAdapter,
        auth_adapter: SecurityAdapter,
    ) -> None:
        self._user = user_adapter
        self._auth = auth_adapter

    async def register_user(self, email: EmailStr | str, password: str) -> Users:
        user = await self._user.get_user_by_email(email=email)
        if user:
            raise UserAlreadyExistsException
        hashed_password = self._auth.get_password_hash(password)
        new_user = Users(email=email, hashed_password=hashed_password)
        await self._user.add_user(new_user)

        return new_user

    async def login_user(self, email: EmailStr | str, password: str) -> str:
        user = await self._user.get_user_by_email(email=email)
        if user is None:
            raise UserNotFoundException
        if not self._auth.verify_password(password, user.hashed_password):
            raise InvalidTokenException
        access_token = await self._auth.create_access_token(data={"sub": str(user.id)})
        return access_token

    async def verify_user_by_token(self, token: str | None) -> Users:
        if token is None:
            raise TokenIsMissingException
        user_id = await self._auth.verify_access_token(token)
        user = await self._user.get_user_by_id(user_id=user_id)
        if not user:
            raise UserNotFoundException

        return user
