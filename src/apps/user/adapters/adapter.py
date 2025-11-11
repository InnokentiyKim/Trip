from src.apps.user.application.exceptions import UserAlreadyExistsException
from src.apps.user.domain.model import User
from src.common.adapters.adapter import SQLAlchemyGateway
from src.common.utils.dependency import SessionDependency
from src.apps.user.application.interfaces.gateway import UserGatewayProto


class UserAdapter(SQLAlchemyGateway, UserGatewayProto):
    async def get_user_by_id(self, user_id) -> User:
        """Retrieve a user by filters."""
        user = await self.get_item_by_id(SessionDependency, User, user_id)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        user = await self.get_one_item(SessionDependency, User, email=email)
        return user

    async def get_users(self, **filters) -> list[User]:
        """Retrieve a list of users."""
        users = await self.get_items_list(SessionDependency, User, **filters)
        return users

    async def add_user(self, user: User) -> None:
        """Add a new user."""
        try:
            await self.add_item(SessionDependency, user)
        except:
            raise UserAlreadyExistsException

    async def delete_user(self, user_id: int) -> None:
        """Delete a user by its ID."""
        user = await self.get_item_by_id(SessionDependency, User, user_id)
        await self.delete_item(SessionDependency, user)
