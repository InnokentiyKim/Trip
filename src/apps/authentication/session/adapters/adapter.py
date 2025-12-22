from datetime import datetime, UTC

from src.apps.authentication.session.application.interfaces.gateway import AuthSessionGatewayProto
from src.apps.authentication.session.domain.models import AuthSession
from src.common.adapters.adapter import SQLAlchemyGateway
from uuid import UUID
from sqlalchemy import select, func


class AuthSessionAdapter(SQLAlchemyGateway, AuthSessionGatewayProto):
    async def add_refresh_session(self, refresh_session: AuthSession):
        self.session.add(refresh_session)

    async def get_refresh_session(
        self,
        hashed_refresh_token: str,
        user_id: UUID,
    ) -> AuthSession | None:
        """
        Retrieves a refresh session from the database.

        Args:
            hashed_refresh_token (str): The hashed refresh token.
            user_id (UUID): The unique identifier of the user.

        Returns:
            AuthSession | None: The refresh session object if found, otherwise None.
        """
        stmt = (
            select(AuthSession)
            .where(
                AuthSession.user_id == user_id,
                AuthSession.hashed_refresh_token == hashed_refresh_token
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_active_auth_session_by_user_id(self, user_id: UUID) -> int:
        """
        Counts the number of active refresh sessions for a user.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            int: The count of active refresh sessions associated with the user.
        """
        stmt = select(func.count(AuthSession.id)).where(
            AuthSession.user_id == user_id,
            AuthSession.expires_at > datetime.now(UTC),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
