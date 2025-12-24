from datetime import datetime, UTC, timedelta

from pydantic import SecretStr

from src.apps.authentication.user.domain import results
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.application.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from src.common.application.service import ServiceBase
from src.apps.authentication.user.domain.models import User
from src.apps.authentication.user.application.ensure import UserServiceInsurance
from src.apps.authentication.user.domain import commands
from src.common.interfaces import SecurityGatewayProto, CustomLoggerProto
from src.apps.authentication.session.domain.enums import AuthTokenTypeEnum
from src.config import Configs


class UserService(ServiceBase):
    def __init__(
        self,
        user_adapter: UserGatewayProto,
        auth_adapter: SecurityGatewayProto,
        user_ensure: UserServiceInsurance,
        logger: CustomLoggerProto,
        config: Configs,
    ) -> None:
        self._user = user_adapter
        self._security = auth_adapter
        self._user_ensure = user_ensure
        self._logger = logger
        self._config = config

    async def create_new_user(self, cmd: commands.CreateUserCommand) -> results.UserInfo:
        """
        This method creates a new user in the system after ensuring that no user with the same
        email already exists. It hashes the provided password before storing it.

        Args:
            cmd (commands.CreateUserCommand): Command object containing user details.

        Returns:
            UserInfo: The created user object.

        Raises:
            UserAlreadyExistsException: If a user with the given email already exists.
        """
        user = await self._user_ensure.user_with_email_exists(cmd.email)
        if user:
            self._logger.error("User with this email already exists", email=cmd.email)
            raise UserAlreadyExistsException

        hashed_password = await self._security.hash_password(cmd.password)
        new_user = User(
            email=cmd.email,
            hashed_password=hashed_password,
            phone=cmd.phone,
            name=cmd.name,
            avatar_url=cmd.avatar_url,
            is_active=cmd.is_active,
        )
        try:
            await self._user.add_user(new_user)
        except Exception as err:
            self._logger.info("User with this email already exists", email=cmd.email)
            raise UserAlreadyExistsException from None

        return results.UserInfo.from_model(new_user)

    async def login_user(self, cmd: commands.LoginUserCommand) -> results.AuthTokens:
        """
        Log in a user and generate authentication tokens.
        This method verifies the user's credentials and, upon successful verification,
        generates access and refresh tokens for the user.

        Args:
            cmd (commands.LoginUserCommand): Command object containing login credentials.

        Returns:
            AuthTokens: An object containing the access and refresh tokens.

        Raises:
            InvalidCredentialsException: If the provided credentials are invalid.
        """
        user = await self._user_ensure.user_with_email_exists(cmd.email)

        if not await self._security.verify_hashed_password(cmd.password, user.hashed_password):
            self._logger.info("Invalid credentials provided", email=cmd.email)
            raise InvalidCredentialsException

        created_at = datetime.now(UTC)
        access_expires_at = created_at + timedelta(minutes=self._config.security.access_token_expire_minutes)
        refresh_expires_at = created_at + timedelta(minutes=self._config.security.refresh_token_expire_minutes)

        access_token = await self._security.create_jwt_token(
            token_type=AuthTokenTypeEnum.ACCESS,
            user_id=user.id,
            created_at=created_at,
            expires_at=access_expires_at,
        )
        refresh_token = await self._security.create_jwt_token(
            token_type=AuthTokenTypeEnum.REFRESH,
            user_id=user.id,
            created_at=created_at,
            expires_at=refresh_expires_at,
        )
        self._logger.info("User logged in successfully", user_id=user.id)

        return results.AuthTokens(access_token=SecretStr(access_token), refresh_token=SecretStr(refresh_token))

    async def verify_user_by_token(self, cmd: commands.VerifyUserByTokenCommand) -> results.UserInfo:
        """
        Verify a user by their access token.
        This method decodes and verifies the provided access token, and retrieves the corresponding user.

        Args:
            cmd (commands.VerifyUserByTokenCommand): Command object containing the access token.

        Returns:
            UserInfo: The user object corresponding to the verified token.

        Raises:
            InvalidTokenException: If the token is invalid or cannot be verified.
        """
        user_id = await self._security.verify_token(cmd.access_token, AuthTokenTypeEnum.ACCESS)
        user = await self._user_ensure.user_exists(user_id)

        return results.UserInfo.from_model(user)
