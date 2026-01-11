from abc import abstractmethod
from uuid import UUID

from src.common.interfaces import GatewayProto
from src.apps.authentication.user.domain.models import User


class UserGatewayProto(GatewayProto):
    @abstractmethod
    async def get_user_by_id(self, user_id) -> User | None:
        """Retrieve a user by filters."""
        ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        ...

    @abstractmethod
    async def get_user_by_phone(self, phone: str) -> User | None:
        """Retrieve a user by phone number."""
        ...

    @abstractmethod
    async def get_users(self, **filters) -> list[User]:
        """Retrieve a list of users."""
        ...

    @abstractmethod
    async def add(self, user: User) -> None:
        """Add a new user."""
        ...

    @abstractmethod
    async def update_user(self, user: User, **params) -> UUID | None:
        """Update an existing user."""
        ...

    @abstractmethod
    async def delete_user(self, user: User) -> None:
        """Delete a user by its ID."""
        ...
