from abc import abstractmethod
from uuid import UUID

from src.apps.authentication.session.domain.models import (
    AuthSession,
    OTPCode,
    PasswordResetToken,
)
from src.common.interfaces import GatewayProto


class AuthSessionGatewayProto(GatewayProto):
    @abstractmethod
    async def add(self, refresh_session: AuthSession):
        """Adds a refresh session to the database."""
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def count_active_auth_session_by_user_id(self, user_id: UUID) -> int:
        """
        Counts the number of active refresh sessions for a user.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            int: The count of active refresh sessions associated with the user.
        """
        ...

    @abstractmethod
    async def remove_refresh_sessions_by_user_id(self, user_id: UUID) -> None:
        """
        Removes all refresh sessions for a user.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        ...

    @abstractmethod
    async def remove(self, auth_session: AuthSession) -> None:
        """
        Removes an auth session from the database.

        Args:
            auth_session (AuthSession): The auth session object.
        """
        ...


class PasswordResetTokenGatewayProto(GatewayProto):
    @abstractmethod
    async def add(self, password_reset_token: PasswordResetToken):
        """Adds a password reset token to the database."""
        ...

    @abstractmethod
    async def get_valid_password_reset_token(self, hashed_token: str) -> PasswordResetToken | None:
        """
        Retrieves a valid password reset token by its hashed value.

        Args:
            hashed_token (str): The hashed password reset token.

        Returns:
            PasswordResetToken | None: The password reset token object if found, otherwise None.
        """
        ...

    @abstractmethod
    async def invalidate_unused_password_reset_tokens(self, user_id: UUID) -> None:
        """
        Invalidates all unused password reset tokens for a user by setting their status as SUPERSEDED.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        ...


class OTPCodeGatewayProto(GatewayProto):
    @abstractmethod
    async def add(self, otp_code: OTPCode) -> None:
        """Adds an OTP code to the database."""
        ...

    @abstractmethod
    async def get_valid_otp_code(self, user_id: UUID) -> OTPCode | None:
        """
        Retrieves a valid OTP code by user ID and purpose.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            OTPCode | None: The OTP code object if found, otherwise None.
        """
        ...

    @abstractmethod
    async def invalidate_unused_otp_codes(self, user_id: UUID) -> None:
        """
        Invalidates all unused OTP codes with the same purpose for a user by setting their status as SUPERSEDED.

        Args:
            user_id (UUID): The unique identifier of the user.
        """
        ...
