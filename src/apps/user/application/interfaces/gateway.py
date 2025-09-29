from abc import abstractmethod

from src.common.interfaces import GatewayProto
from src.apps.user.domain.model import User


class UserGatewayProto(GatewayProto):
    @abstractmethod
    async def get_user_by_id(self, user_id) -> User:
        """Retrieve a user by filters."""
        ...

    @abstractmethod
    async def get_users(self, **filters) -> list[User]:
        """Retrieve a list of users."""
        ...

    @abstractmethod
    async def add_user(self, user: User) -> None:
        """Add a new user."""
        ...

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        """Delete a user by its ID."""
        ...
