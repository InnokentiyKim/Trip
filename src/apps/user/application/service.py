from fastapi import HTTPException

from src.apps.authentication.adapters.adapter import AuthenticationAdapter
from src.apps.user.adapters.adapter import UserAdapter
from common.application.service import ServiceBase
from src.apps.user.domain.model import Users


class UserService(ServiceBase):
    def __init__(
        self,
        user_adapter: UserAdapter,
        auth_adapter: AuthenticationAdapter,
    ) -> None:
        self._user = user_adapter
        self._auth = auth_adapter

    async def register_user(self, email: str, password: str) -> None:
        user = await self._user.get_user_by_email(email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        hashed_password = self._auth.get_password_hash(password)
        new_user = Users(email=email, hashed_password=hashed_password)
        await self._user.add_user(new_user)
