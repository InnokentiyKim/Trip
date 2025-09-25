from apps.user.application.exceptions import UserAlreadyExistsException
from apps.user.domain.model import Users
from common.adapters.adapter import SQLAlchemyGateway
from common.utils.dependency import SessionDependency
from src.apps.user.application.interfaces.gateway import UserGatewayProto


class UserAdapter(SQLAlchemyGateway, UserGatewayProto):
    async def get_user_by_id(self, user_id) -> Users:
        """Retrieve a user by filters."""
        user = await self.get_item_by_id(SessionDependency, Users, user_id)
        return user

    async def get_user_by_email(self, email: str) -> Users | None:
        """Retrieve a user by email."""
        user = await self.get_one_item(SessionDependency, Users, email=email)
        return user

    async def get_users(self, **filters) -> list[Users]:
        """Retrieve a list of users."""
        users = await self.get_items_list(SessionDependency, Users, **filters)
        return users

    async def add_user(self, user: Users) -> None:
        """Add a new user."""
        try:
            await self.add_item(SessionDependency, user)
        except:
            raise UserAlreadyExistsException

    async def delete_user(self, user_id: int) -> None:
        """Delete a user by its ID."""
        user = await self.get_item_by_id(SessionDependency, Users, user_id)
        await self.delete_item(SessionDependency, user)
