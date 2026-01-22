from typing import Any
from uuid import UUID

from src.apps.authentication.user.application.exceptions import (
    UserAlreadyExistsError,
)
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.domain.models import User
from src.common.adapters.adapter import FakeGateway, SQLAlchemyGateway


class UserAdapter(SQLAlchemyGateway, UserGatewayProto):
    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieve a user by filters.

        Args:
            user_id (UUID): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, else None.
        """
        user = await self.get_item_by_id(User, user_id)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The user if found, else None.
        """
        user = await self.get_one_item(User, email=email)
        return user

    async def get_user_by_phone(self, phone: str) -> User | None:
        """
        Retrieve a user by phone number.

        Args:
            phone (str): The phone number of the user to retrieve.

        Returns:
            User | None: The user if found, else None.
        """
        user = await self.get_one_item(User, phone=phone)
        return user

    async def get_users(self, **filters: Any) -> list[User]:
        """
        Retrieve a list of users.

        Args:
            **filters: Filters to apply to the users query.

        Returns:
            list[User]: A list of users matching the filters.
        """
        users = await self.get_items_list(User, **filters)
        return users

    async def add(self, user: User) -> None:
        """
        Add a new user.

        Args:
            user (User): The user to add.

        Raises:
            UserAlreadyExistsError: If a user with the same unique fields already exists.
        """
        try:
            self.session.add(user)
            await self.session.commit()
        except Exception:
            raise UserAlreadyExistsError from None

    async def update_user(self, user: User, **params: Any) -> UUID | None:
        """
        Update an existing user.

        Args:
            user (User): The user to update.
            **params: The fields to update with their new values.

        Returns:
            UUID | None: The ID of the updated user, or None if update failed.
        """
        for key, value in params.items():
            setattr(user, key, value)
        await self.add(user)
        return user.id

    async def delete_user(self, user: User) -> None:
        """
        Delete a user by its ID.

        Args:
            user (User): The user to delete.

        Returns:
            None
        """
        await self.delete_item(user)


class FakeUserAdapter(FakeGateway[User], UserGatewayProto):
    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Retrieve a user by filters."""
        return next((user for user in self._collection if user.id == user_id), None)

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        return next((user for user in self._collection if user.email == email), None)

    async def get_user_by_phone(self, phone: str) -> User | None:
        """Retrieve a user by phone number."""
        return next((user for user in self._collection if user.phone == phone), None)

    async def get_users(self, **filters: Any) -> list[User]:
        """Retrieve a list of users."""
        return [user for user in self._collection if all(getattr(user, k) == v for k, v in filters.items())]

    async def add(self, user: User) -> None:
        """Add a new user."""
        self._collection.add(user)

    async def update_user(self, user: User, **params: Any) -> UUID | None:
        """Update an existing user."""
        for key, value in params.items():
            setattr(user, key, value)

        self._collection.discard(user)
        self._collection.add(user)

        return user.id or None

    async def delete_user(self, user: User) -> None:
        """Delete a user by its ID."""
        self._collection.discard(user)
