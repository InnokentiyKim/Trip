from typing import Annotated

from src.apps.authentication.user.domain import results
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.application.exceptions import UserAlreadyExistsException, InvalidInputValuesException, \
    InvalidCredentialsException
from src.apps.authentication.user.domain.enums import UserTypeEnum
from src.apps.authentication.user.domain.fetches import GetUserInfo
from src.apps.authorization.role.application.service import RoleManagementService
from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.apps.authorization.role.domain.fetches import GetRoleInfoByName
from src.apps.authorization.role.domain.results import RoleInfo
from src.common.application.service import ServiceBase
from src.apps.authentication.user.domain.models import User
from src.apps.authentication.user.application.ensure import UserServiceEnsurance
from src.apps.authentication.user.domain import commands
from src.common.interfaces import SecurityGatewayProto, CustomLoggerProto
from src.config import Configs


class UserService(ServiceBase):
    def __init__(
        self,
        user_adapter: UserGatewayProto,
        security_adapter: SecurityGatewayProto,
        user_ensure: UserServiceEnsurance,
        role_management: RoleManagementService,
        logger: CustomLoggerProto,
        config: Configs,
    ) -> None:
        self._user = user_adapter
        self._security = security_adapter
        self._user_ensure = user_ensure
        self._role_management = role_management
        self._logger = logger
        self._config = config

    async def _get_role_from_user_type(self, user_type: UserTypeEnum) -> RoleInfo:
        allowed_types = {UserTypeEnum.USER, UserTypeEnum.MANAGER}

        if user_type not in allowed_types:
            self._logger.error("Invalid user type provided", user_type=user_type)
            raise InvalidInputValuesException

        role_name: Annotated[UserRoleEnum, UserTypeEnum] = UserRoleEnum(user_type.value)
        role_info = await self._role_management.get_role_info_by_name(
            fetch=GetRoleInfoByName(role_name=role_name)
        )

        return role_info


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

        hashed_password = await self._security.hash_password(cmd.password.get_secret_value())
        role_info = await self._get_role_from_user_type(cmd.user_type)

        new_user = User(
            email=cmd.email,
            hashed_password=hashed_password,
            role=role_info.id,
            phone=cmd.phone,
            name=cmd.name,
            avatar_url=cmd.avatar_url,
            is_active=cmd.is_active,
        )
        await self._user.add(new_user)

        return results.UserInfo.from_model(new_user)

    async def verify_user_credentials(self, cmd: commands.VerifyUserCredentialsCommand) -> results.UserInfo:
        """
        Validates password authentication credentials and returns the user ID.

        Args:
            cmd (commands.ValidatePasswordCredentials): The command containing the credentials to validate.

        Returns:
            results.UserID: A data structure containing the ID of the successfully authenticated user.

        Raises:
            InvalidCredentialsError: If no user is found for the provided email, or if the password verification fails.
        """
        user = await self._user_ensure.user_with_email_exists(email=cmd.email)

        if not user.hashed_password:
            raise InvalidCredentialsException

        if not await self._security.verify_hashed_password(
            plain_password=cmd.password.get_secret_value(),
            hashed_password=user.hashed_password,
        ):
            self._logger.warning("Incorrect password for user", user_id=user.id)
            raise InvalidCredentialsException

        return results.UserInfo.from_model(user)

    async def get_user_info(self, fetch: GetUserInfo):
        """
        Retrieve user information by user ID.

        Args:
            fetch (GetUserInfo): Object containing the user ID to fetch.

        Returns:
            UserInfo: The user object corresponding to the provided user ID.

        Raises:
            UserIsNotFoundError: If the user does not exist.
        """
        user = await self._user_ensure.user_exists(fetch.user_id)
        return results.UserInfo.from_model(user)
