from uuid import UUID

from src.apps.authentication.session.application.interfaces.gateway import (
    AuthSessionGatewayProto, PasswordResetTokenGatewayProto, OTPCodeGatewayProto
)
from src.apps.authentication.session.domain.models import AuthSession, PasswordResetToken, OTPCode
from src.common.interfaces import CustomLoggerProto
import src.apps.authentication.session.application.exceptions as auth_exceptions


class AuthenticationServiceEnsurance:
    def __init__(
        self,
        auth_sessions: AuthSessionGatewayProto,
        password_reset_tokens: PasswordResetTokenGatewayProto,
        otp_codes: OTPCodeGatewayProto,
        logger: CustomLoggerProto,
    ) -> None:
        self._auth_sessions = auth_sessions
        self._password_reset_tokens = password_reset_tokens
        self._otp_codes = otp_codes
        self._logger = logger

    async def auth_session_exists(
        self,
        hashed_refresh_token: str,
        user_id: UUID,
    ) -> AuthSession:
        """
        Checks if a refresh session exists for the provided parameters.

        Args:
            hashed_refresh_token (str): The hashed refresh token.
            user_id (UUID): The unique identifier of the user.

        Returns:
            RefreshSession: The refresh session object if it exists.

        Raises:
            InvalidRefreshSessionError: If the refresh session does not exist.
        """
        auth_session = await self._auth_sessions.get_refresh_session(hashed_refresh_token, user_id)

        if auth_session is None:
            self._logger.debug("Could not find auth session", user_id=user_id)
            raise auth_exceptions.InvalidRefreshSessionError

        return auth_session

    async def valid_password_reset_token_exists(self, hashed_token: str) -> PasswordResetToken:
        """
        Checks if a valid password reset token exists for the provided hashed token.

        Args:
            hashed_token (str): The hashed password reset token.

        Returns:
            PasswordResetToken: The password reset token object if it exists.

        Raises:
            InvaliPasswordResetTokenError: If the password reset token does not exist.
        """
        password_reset_token = await self._password_reset_tokens.get_valid_password_reset_token(hashed_token)

        if password_reset_token is None:
            self._logger.debug("Could not find valid password reset token")
            raise auth_exceptions.InvalidPasswordResetTokenError

        return password_reset_token

    async def valid_otp_code_exists(self, user_id: UUID) -> OTPCode:
        """
        Checks if a valid OTP code exists for the provided user ID and purpose.

        Args:
            user_id (UUID): The unique identifier of the user.

        Returns:
            OTPCode: The OTP code object if it exists and is valid.

        Raises:
            InvalidOTPCodeError: If the OTP code does not exist or is invalid.
        """
        otp_code = await self._otp_codes.get_valid_otp_code(user_id)

        if otp_code is None:
            self._logger.debug("Could not find valid OTP code", user_id=user_id)
            raise auth_exceptions.InvalidOTPCodeError

        return otp_code
