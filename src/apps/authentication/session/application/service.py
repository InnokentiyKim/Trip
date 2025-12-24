import uuid
from datetime import datetime, UTC, timedelta

from pydantic import SecretStr

from src.apps.authentication.session.application.ensure import AuthenticationServiceEnsurance
from src.apps.authentication.session.application.interfaces.gateway import AuthSessionGatewayProto, \
    PasswordResetTokenGatewayProto, OTPCodeGatewayProto
from src.apps.authentication.session.domain.commands import CreateAuthSessionCommand, ConsumeRefreshTokenCommand, \
    InvalidateRefreshTokenCommand, CreatePasswordResetTokenCommand, ConfirmPasswordResetCommand, CreateOTPCodeCommand, \
    ConsumeOTPCodeCommand, CreateMFATokenCommand, ValidateMFATokenCommand
from src.apps.authentication.session.domain.enums import OTPStatusEnum, AuthTokenTypeEnum, PasswordResetTokenStatusEnum
from src.apps.authentication.session.domain.models import OTPCode, AuthSession, PasswordResetToken
from src.common.application.service import ServiceBase
from src.common.interfaces import SecurityGatewayProto, CustomLoggerProto
from src.config import Configs
import src.apps.authentication.session.application.exceptions as auth_exceptions
from src.apps.authentication.session.domain import results


class AuthenticationService(ServiceBase):
    def __init__(
        self,
        security: SecurityGatewayProto,
        auth_sessions: AuthSessionGatewayProto,
        password_reset_tokens: PasswordResetTokenGatewayProto,
        otp_codes: OTPCodeGatewayProto,
        config: Configs,
        logger: CustomLoggerProto,
    ) -> None:
        self._security = security
        self._auth_sessions = auth_sessions
        self._password_reset_tokens = password_reset_tokens
        self._otp_codes = otp_codes
        self._config = config
        self._logger = logger

        self._ensure = AuthenticationServiceEnsurance(
            auth_sessions,
            password_reset_tokens,
            otp_codes,
            logger,
        )

    async def _validate_otp_code(self, plain_code: str, otp_code: OTPCode) -> None:
        """
        Validates an OTP code against a stored hashed code and handles failed attempts.

        Args:
            plain_code (str): The plain text OTP code to validate.
            otp_code (OTPCode): The OTP code entity containing the hashed code to compare against.

        Raises:
            OTPMaxAttemptsExceededError: If the maximum number of failed attempts is reached.
            InvalidOTPCodeError: If the provided OTP code is invalid.
        """
        # Check for fake OTP bypass
        if self._config.auth.bypass_otp_code_enabled:
            if plain_code == self._config.auth.bypass_otp_code:
                return

        is_valid = self._security.verify_hashed_string(plain_code, otp_code.hashed_otp_code)
        if not is_valid:
            self._logger.warning("Invalid OTP provided for user ID", user_id=otp_code.user_id)
            otp_code.failed_attempts += 1

            if otp_code.failed_attempts >= self._config.auth.otp_max_attempts:
                self._logger.error(
                    "OTP for user ID permanently failed after reaching max attempts.",
                    user_id=otp_code.user_id,
                )
                otp_code.status = OTPStatusEnum.FAILED
                raise auth_exceptions.OTPMaxAttemptsExceededError

            raise auth_exceptions.InvalidOTPCodeError

    async def create_auth_session(self, cmd: CreateAuthSessionCommand) -> results.AuthTokens:
        """
        Generates authentication tokens and creates a refresh session for a user.

        Args:
            cmd (commands.CreateRefreshSession): The command containing refresh session information.

        Returns:
            results.AuthTokens: A data structure containing the access and refresh tokens.
        """
        now = datetime.now(UTC)

        access_token = await self._security.create_jwt_token(
            token_type=AuthTokenTypeEnum.ACCESS,
            user_id=cmd.user_id,
            created_at=now,
            expires_at=now + timedelta(minutes=self._config.security.access_token_expire_minutes)
        )
        refresh_token = await self._security.create_jwt_token(
            token_type=AuthTokenTypeEnum.REFRESH,
            user_id=cmd.user_id,
            created_at=now,
            expires_at=now + timedelta(days=self._config.security.refresh_token_expire_minutes)
        )
        hashed_refresh_token = self._security.hash_string(refresh_token)
        auth_session = AuthSession(
            user_id=cmd.user_id,
            hashed_refresh_token=hashed_refresh_token,
            duration=timedelta(minutes=self._config.security.refresh_token_expire_minutes),
            created_at=now,
        )
        await self._auth_sessions.add(auth_session)
        return results.AuthTokens(
            access_token=SecretStr(access_token),
            refresh_token=SecretStr(refresh_token),
        )

    async def consume_refresh_token(self, cmd: ConsumeRefreshTokenCommand) -> results.UserID:
        """
        Validates and consumes a refresh token, returning the user ID.

        Args:
            cmd (commands.ConsumeRefreshToken): The command containing the refresh token and fingerprint.

        Returns:
            results.UserID: A data structure containing the ID of the user from the validated session.

        Raises:
            InvalidRefreshSessionError: If the token is invalid or the fingerprint does not match.
        """
        refresh_token = cmd.refresh_token.get_secret_value()
        # Verify the refresh token and extract the user ID
        user_id = await self._security.verify_token(refresh_token, AuthTokenTypeEnum.REFRESH)
        hashed_refresh_token = self._security.hash_string(refresh_token)
        auth_session = await self._ensure.auth_session_exists(hashed_refresh_token, user_id)
        is_expired = datetime.now(UTC) >= auth_session.expires_at
        # Remove the auth session if the refresh token is expired
        await self._auth_sessions.remove(auth_session)
        # Check if the refresh token is expired
        if is_expired:
            self._logger.warning("Consumed an expired refresh session for user", user_id=user_id)
            raise auth_exceptions.InvalidRefreshSessionError

        return results.UserID(id=user_id)

    async def invalidate_refresh_token(self, cmd: InvalidateRefreshTokenCommand) -> None:
        """
        Invalidates a refresh token by removing the refresh session.

        Args:
            cmd (commands.InvalidateRefreshTokenCommand): The command containing the refresh token.

        Raises:
            InvalidRefreshSessionError: If the token is invalid.
        """
        refresh_token = cmd.refresh_token.get_secret_value()
        # Verify the refresh token and extract the user ID
        user_id = await self._security.verify_token(refresh_token, AuthTokenTypeEnum.REFRESH)
        hashed_refresh_token = self._security.hash_string(refresh_token)
        auth_session = await self._auth_sessions.get_refresh_session(hashed_refresh_token, user_id)

        if not auth_session:
            self._logger.debug("No refresh session found to invalidate", user_id=user_id)

        # Remove the auth session to invalidate the refresh token
        await self._auth_sessions.remove(auth_session)
        self._logger.debug("Refresh token successfully invalidated", user_id=user_id)

    async def create_password_reset_token(self, cmd: CreatePasswordResetTokenCommand) -> results.PasswordResetTokenInfo:
        """
        Creates a password reset token for a user.

        Args:
            cmd (commands.CreatePasswordResetToken): The command containing the user ID.

        Returns:
            results.PasswordResetTokenWithSecret: A data structure containing the password reset token
                and its associated information.
        """
        now = datetime.now(UTC)
        reset_token = self._security.generate_urlsafe_token()
        hashed_reset_token = self._security.hash_string(reset_token)
        await self._password_reset_tokens.invalidate_unused_password_reset_tokens(cmd.user_id)

        expires_at = now + timedelta(minutes=self._config.auth.reset_password_token_lifetime_minutes)
        password_reset_token = PasswordResetToken(
            id=uuid.uuid4(),
            user_id=cmd.user_id,
            hashed_refresh_token=hashed_reset_token,
            created_at=now,
            expires_at=expires_at,
            status=PasswordResetTokenStatusEnum.CREATED
        )
        await self._password_reset_tokens.add(password_reset_token)
        password_reset_token_info = results.PasswordResetTokenInfo(
            id=password_reset_token.id,
            user_id=password_reset_token.user_id,
            reset_token=SecretStr(reset_token),
            hashed_reset_token=password_reset_token.hashed_refresh_token,
            created_at=password_reset_token.created_at,
            expires_at=password_reset_token.expires_at,
            status=password_reset_token.status
        )

        return password_reset_token_info

    async def confirm_password_reset(self, cmd: ConfirmPasswordResetCommand) -> results.UserID:
        """
        Confirms a password reset by validating the reset token and updating the user's password.

        Args:
            cmd (commands.ConfirmPasswordReset): The command containing the password reset token and new password.

        Returns:
            results.UserID: A data structure containing the ID of the user whose password was reset.

        Raises:
            InvalidPasswordResetTokenError: If the password reset token is invalid or expired.
        """
        hashed_reset_token = self._security.hash_string(cmd.password_reset_token.get_secret_value())
        password_reset_token = await self._ensure.valid_password_reset_token_exists(hashed_reset_token)
        user_id = password_reset_token.user_id

        # Mark the password reset token as VERIFIED
        password_reset_token.status = PasswordResetTokenStatusEnum.VERIFIED
        await self._password_reset_tokens.add(password_reset_token)

        return results.UserID(id=user_id)

    async def create_otp_code(self, cmd: CreateOTPCodeCommand) -> results.OTPCodeInfo:
        """
        Creates a one-time password (OTP) for a specific purpose and recipient.

        Args:
            cmd (commands.CreateOTPCode): The command containing the user ID and recipient and purpose.

        Returns:
            results.OTPCodeWithSecret: A data structure containing the OTP code and its associated information.
        """
        now = datetime.now(UTC)
        self._logger.info(
            "Creating OTP code for user with purpose for recipient",
            user_id=cmd.user_id,
            recipient=cmd.recipient,
        )

        plain_code = self._security.generate_otp_code()
        hashed_plain_code = self._security.hash_string(plain_code)

        # Invalidate any existing unused OTP codes for the user
        await self._otp_codes.invalidate_unused_otp_codes(cmd.user_id)

        otp_expires_at = now + timedelta(minutes=self._config.auth.otp_lifetime_minutes)
        otp_code = OTPCode(
            id=uuid.uuid4(),
            user_id=cmd.user_id,
            hashed_otp_code=hashed_plain_code,
            failed_attempts=0,
            channel=cmd.channel,
            created_at=now,
            expires_at=otp_expires_at,
            status=OTPStatusEnum.CREATED,
        )
        await self._otp_codes.add(otp_code)

        self._logger.info("OTP code successfully created", user_id=cmd.user_id)
        otp_code_info = results.OTPCodeInfo(
            id=otp_code.id,
            user_id=otp_code.user_id,
            channel=otp_code.channel,
            otp_code=plain_code,
            hashed_otp_code=otp_code.hashed_otp_code,
            failed_attempts=otp_code.failed_attempts,
            created_at=otp_code.created_at,
            expires_at=otp_code.expires_at,
            status=otp_code.status
        )

        return otp_code_info

    async def consume_otp_code(self, cmd: ConsumeOTPCodeCommand) -> results.UserID:
        """
        Consumes an OTP code for a specific user and purpose.

        Args:
            cmd (commands.ConsumeOTPCodeByUserID): The command containing the user ID, purpose, and OTP code.

        Returns:
            results.UserID: A data structure containing the ID of the user whose OTP was consumed.

        Raises:
            InvalidOTPCodeError: If the provided OTP code is invalid.
            OTPMaxAttemptsExceededError: If the maximum number of failed attempts is reached.
        """
        otp_code = await self._ensure.valid_otp_code_exists(cmd.user_id)
        await self._validate_otp_code(cmd.plain_code.get_secret_value(), otp_code)

        # Mark the OTP code as VERIFIED
        otp_code.status = OTPStatusEnum.VERIFIED
        await self._otp_codes.add(otp_code)

        return results.UserID(id=otp_code.user_id)

    async def create_mfa_token(self, cmd: CreateMFATokenCommand) -> results.MFAToken:
        """
        Creates an MFA token for a user.

        Args:
            cmd (commands.CreateMFAToken): The command containing the user ID.

        Returns:
            results.MFAToken: A data structure containing the MFA token and user ID.
        """
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=self._config.auth.mfa_token_lifetime_minutes)

        mfa_token = await self._security.create_jwt_token(
            token_type=AuthTokenTypeEnum.MFA,
            user_id=cmd.user_id,
            created_at=now,
            expires_at=expires_at,
        )
        return results.MFAToken(SecretStr(mfa_token))

    async def validate_mfa_token(self, cmd: ValidateMFATokenCommand) -> results.UserID:
        """
        Validates MFA token and returns the user ID.

        Args:
            cmd (commands.ValidateMFAToken): The command containing the MFA token.

        Returns:
            results.UserID: A data structure containing the ID of the user.
        """
        self._logger.info("Validating MFA token", user_id=cmd.user_id)
        plain_mfa_token = cmd.mfa_token.get_secret_value()

        # Validate the MFA token and extract the user ID
        user_id = await self._security.verify_token(plain_mfa_token, AuthTokenTypeEnum.MFA)

        self._logger.info("MFA token validated for channel selection", user_id=user_id)
        return results.UserID(user_id)
