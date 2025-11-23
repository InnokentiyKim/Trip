from uuid import UUID

from src.apps.user.application.exceptions import UserAlreadyExistsException
from src.apps.user.domain.models import User
from src.common.adapters.adapter import SQLAlchemyGateway
from src.apps.user.application.interfaces.gateway import UserGatewayProto


class UserAdapter(SQLAlchemyGateway, UserGatewayProto):
    async def get_user_by_id(self, user_id) -> User:
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

    async def add_user(self, user: User) -> None:
        """Add a new user."""
        try:
            self.session.add(user)
            await self.session.commit()
        except:
            raise UserAlreadyExistsException

    async def update_user(self, user: User, **params) -> UUID | None:
        """Update an existing user."""
        for key, value in params.items():
            setattr(user, key, value)
        await self.add_item(user)
        return user.id

    async def delete_user(self, user: User) -> None:
        """Delete a user by its ID."""
        await self.delete_item(user)
