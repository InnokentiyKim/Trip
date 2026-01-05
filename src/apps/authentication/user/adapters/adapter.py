from uuid import UUID

from src.apps.authentication.user.application.exceptions import UserAlreadyExistsException
from src.apps.authentication.user.domain.models import User
from src.common.adapters.adapter import SQLAlchemyGateway, FakeGateway
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto


class UserAdapter(SQLAlchemyGateway, UserGatewayProto):
    async def get_user_by_id(self, user_id) -> User | None:
        """Retrieve a user by filters."""
        user = await self.get_item_by_id(User, user_id)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        user = await self.get_one_item(User, email=email)
        return user

    async def get_users(self, **filters) -> list[User]:
        """Retrieve a list of users."""
        users = await self.get_items_list(User, **filters)
        return users

    async def add(self, user: User) -> None:
        """Add a new user."""
        try:
            self.session.add(user)
            await self.session.commit()
        except Exception:
            raise UserAlreadyExistsException

    async def update_user(self, user: User, **params) -> UUID | None:
        """Update an existing user."""
        for key, value in params.items():
            setattr(user, key, value)
        await self.add(user)
        return user.id

    async def delete_user(self, user: User) -> None:
        """Delete a user by its ID."""
        await self.delete_item(user)


class FakeUserAdapter(FakeGateway, UserGatewayProto):
    async def get_user_by_id(self, user_id) -> User | None:
        """Retrieve a user by filters."""
        return next((user for user in self._collection if user.id == user_id), None)

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        return next((user for user in self._collection if user.email == email), None)

    async def get_users(self, **filters) -> list[User]:
        """Retrieve a list of users."""
        return [
            user for user in self._collection if all(getattr(user, k) == v for k, v in filters.items())
        ]

    async def add(self, user: User) -> None:
        """Add a new user."""
        self._collection.add(user)

    async def update_user(self, user: User, **params) -> UUID | None:
        """Update an existing user."""
        for key, value in params.items():
            setattr(user, key, value)

        self._collection.discard(user)
        self._collection.add(user)

        return user.id or None

    async def delete_user(self, user: User) -> None:
        """Delete a user by its ID."""
        self._collection.discard(user)
