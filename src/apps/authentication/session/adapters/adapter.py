from datetime import datetime, UTC

from src.apps.authentication.session.application.interfaces.gateway import AuthSessionGatewayProto
from src.apps.authentication.session.domain.enums import PasswordResetTokenStatusEnum
from src.apps.authentication.session.domain.models import AuthSession, PasswordResetToken, OTPCode
from src.common.adapters.adapter import SQLAlchemyGateway
from uuid import UUID
from sqlalchemy import select, delete, update, func


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

    async def remove_refresh_sessions_by_user_id(self, user_id: UUID) -> None:
        """
        Removes all refresh sessions for a user.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        stmt = delete(AuthSession).where(AuthSession.user_id == user_id)
        await self.session.execute(stmt)


class PasswordResetTokenAdapter(SQLAlchemyGateway):
    async def add(self, password_reset_token: PasswordResetToken):
        """Adds a password reset token to the database."""
        self.session.add(password_reset_token)

    async def get_valid_password_reset_token(self, hashed_token: str) -> PasswordResetToken | None:
        """
        Retrieves a valid password reset token by its hashed value.

        Args:
            hashed_token (str): The hashed password reset token.

        Returns:
            PasswordResetToken | None: The password reset token object if found, otherwise None.
        """
        stmt = (
            select(PasswordResetToken).where(
                PasswordResetToken.hashed_refresh_token == hashed_token,
                PasswordResetToken.status == PasswordResetTokenStatusEnum.CREATED,
                PasswordResetToken.expires_at > datetime.now(UTC),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def invalidate_unused_password_reset_tokens(self, user_id: UUID) -> None:
        """
        Invalidates all unused password reset tokens for a user by setting their status as SUPERSEDED.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        stmt = (
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.status == PasswordResetTokenStatusEnum.CREATED
            )
            .values(PasswordResetTokenStatusEnum.SUPERSEDED)
        )
        await self.session.execute(stmt)


class OTPCodeAdapter(SQLAlchemyGateway):
    async def add(self, otp_code: OTPCode) -> None:
        """Adds an OTP code to the database."""
        self.session.add(otp_code)

    async def get_valid_otp_code(self, user_id: UUID) -> OTPCode | None:
        """
        Retrieves a valid OTP code by user ID and purpose.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            OTPCode | None: The OTP code object if found, otherwise None.
        """
        stmt = (
            select(OTPCode)
            .where(
                OTPCode.user_id == user_id,
                OTPCode.status == PasswordResetTokenStatusEnum.CREATED,
                OTPCode.expires_at > datetime.now(UTC),
            )
            .order_by(OTPCode.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def invalidate_unused_otp_codes(self, user_id: UUID) -> None:
        """
        Invalidates all unused OTP codes with the same purpose for a user by setting their status as SUPERSEDED.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        stmt = (
            update(OTPCode)
            .where(
                OTPCode.user_id == user_id,
                OTPCode.status == PasswordResetTokenStatusEnum.CREATED
            )
            .values(status=PasswordResetTokenStatusEnum.SUPERSEDED)
        )
        await self.session.execute(stmt)
