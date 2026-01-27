from abc import ABC
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, func, select, update

from src.apps.authentication.session.application.interfaces.gateway import (
    AuthSessionGatewayProto,
    OTPCodeGatewayProto,
    PasswordResetTokenGatewayProto,
)
from src.apps.authentication.session.domain.enums import (
    OTPStatusEnum,
    PasswordResetTokenStatusEnum,
)
from src.apps.authentication.session.domain.models import (
    AuthSession,
    OTPCode,
    PasswordResetToken,
)
from src.common.adapters.adapter import FakeGateway, SQLAlchemyGateway


class AuthSessionAdapter(SQLAlchemyGateway, AuthSessionGatewayProto, ABC):
    async def add(self, refresh_session: AuthSession) -> None:
        """Adds a refresh session to the database."""
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
                AuthSession.hashed_refresh_token == hashed_refresh_token,
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

    async def remove(self, auth_session: AuthSession) -> None:
        """
        Removes an auth session from the database.

        Args:
            auth_session (AuthSession): The auth session object.
        """
        await self.session.delete(auth_session)


class PasswordResetTokenAdapter(SQLAlchemyGateway, PasswordResetTokenGatewayProto):
    async def add(self, password_reset_token: PasswordResetToken) -> None:
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
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.hashed_reset_token == hashed_token,
            PasswordResetToken.status == PasswordResetTokenStatusEnum.CREATED,
            PasswordResetToken.expires_at > datetime.now(UTC),
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
                PasswordResetToken.status == PasswordResetTokenStatusEnum.CREATED,
            )
            .values(PasswordResetTokenStatusEnum.SUPERSEDED)
        )
        await self.session.execute(stmt)


class OTPCodeAdapter(SQLAlchemyGateway, OTPCodeGatewayProto):
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
                OTPCode.status == PasswordResetTokenStatusEnum.CREATED,
            )
            .values(status=PasswordResetTokenStatusEnum.SUPERSEDED)
        )
        await self.session.execute(stmt)


class FakeAuthSessionAdapter(FakeGateway[AuthSession], AuthSessionGatewayProto):
    async def add(self, refresh_session: AuthSession) -> None:
        """Adds a refresh session to the database."""
        self._collection.add(refresh_session)

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
        return next(
            (
                auth_session
                for auth_session in self._collection
                if auth_session.user_id == user_id and auth_session.hashed_refresh_token == hashed_refresh_token
            ),
            None,
        )

    async def count_active_auth_session_by_user_id(self, user_id: UUID) -> int:
        """
        Counts the number of active refresh sessions for a user.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            int: The count of active refresh sessions associated with the user.
        """
        from datetime import UTC, datetime

        return sum(
            1
            for auth_session in self._collection
            if auth_session.user_id == user_id and auth_session.expires_at > datetime.now(UTC)
        )

    async def remove_refresh_sessions_by_user_id(self, user_id: UUID) -> None:
        """
        Removes all refresh sessions for a user.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        self._collection = {auth_session for auth_session in self._collection if auth_session.user_id != user_id}

    async def remove(self, auth_session: AuthSession) -> None:
        """
        Removes an auth session from the database.

        Args:
            auth_session (AuthSession): The auth session object.
        """
        self._collection.discard(auth_session)


class FakePasswordResetTokenAdapter(FakeGateway[PasswordResetToken], PasswordResetTokenGatewayProto):
    async def add(self, password_reset_token: PasswordResetToken) -> None:
        """Adds a password reset token to the database."""
        self._collection.add(password_reset_token)

    async def get_valid_password_reset_token(self, hashed_token: str) -> PasswordResetToken | None:
        """
        Retrieves a valid password reset token by its hashed value.

        Args:
            hashed_token (str): The hashed password reset token.

        Returns:
            PasswordResetToken | None: The password reset token object if found, otherwise None.
        """
        from datetime import UTC, datetime

        return next(
            (
                token
                for token in self._collection
                if token.hashed_reset_token == hashed_token
                and token.status == PasswordResetTokenStatusEnum.CREATED
                and token.expires_at > datetime.now(UTC)
            ),
            None,
        )

    async def invalidate_unused_password_reset_tokens(self, user_id: UUID) -> None:
        """
        Invalidates all unused password reset tokens for a user by setting their status as SUPERSEDED.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        to_replace = []

        for token in self._collection:
            if token.user_id == user_id and token.status == PasswordResetTokenStatusEnum.CREATED:
                new_token = PasswordResetToken(
                    id=token.id,
                    user_id=token.user_id,
                    hashed_reset_token=token.hashed_reset_token,
                    created_at=token.created_at,
                    expires_at=token.expires_at,
                    status=PasswordResetTokenStatusEnum.SUPERSEDED,
                )
                to_replace.append((token, new_token))

        for old_token, new_token in to_replace:
            self._collection.discard(old_token)
            self._collection.add(new_token)


class FakeOTPCodeAdapter(FakeGateway[OTPCode], OTPCodeGatewayProto):
    async def add(self, otp_code: OTPCode) -> None:
        """Adds an OTP code to the database."""
        self._collection.add(otp_code)

    async def get_valid_otp_code(self, user_id: UUID) -> OTPCode | None:
        """
        Retrieves a valid OTP code by user ID and purpose.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            OTPCode | None: The OTP code object if found, otherwise None.
        """
        from datetime import UTC, datetime

        valid_codes = [
            code
            for code in self._collection
            if code.user_id == user_id and code.status == OTPStatusEnum.CREATED and code.expires_at > datetime.now(UTC)
        ]

        if not valid_codes:
            return None

        # Return the most recently created code
        return max(valid_codes, key=lambda code: code.created_at)

    async def invalidate_unused_otp_codes(self, user_id: UUID) -> None:
        """
        Invalidates all unused OTP codes with the same purpose for a user by setting their status as SUPERSEDED.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        to_replace = []

        for code in self._collection:
            if code.user_id == user_id and code.status == OTPStatusEnum.CREATED:
                new_code = OTPCode(
                    id=code.id,
                    user_id=code.user_id,
                    hashed_otp_code=code.hashed_otp_code,
                    created_at=code.created_at,
                    expires_at=code.expires_at,
                    status=OTPStatusEnum.SUPERSEDED,
                    failed_attempts=code.failed_attempts,
                    channel=code.channel,
                )
                to_replace.append((code, new_code))

        for old_code, new_code in to_replace:
            self._collection.discard(old_code)
            self._collection.add(new_code)
