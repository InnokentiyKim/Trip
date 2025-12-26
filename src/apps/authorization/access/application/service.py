from src.apps.authentication.user.application.ensure import UserServiceInsurance
from src.apps.authorization.access.application.interfaces.gateway import AccessGatewayProto
from src.apps.authorization.access.domain import commands
from src.apps.authentication.session.domain.enums import AuthTokenTypeEnum
from src.apps.authorization.access.domain.results import UserAccessInfo
from src.apps.authorization.access.domain.exceptions import Forbidden
from src.common.application.service import ServiceBase
from src.common.interfaces import SecurityGatewayProto, CustomLoggerProto
from src.apps.authentication.user.domain.results import UserInfo
from src.config import Configs


class AccessService(ServiceBase):
    def __init__(
        self,
        security_adapter: SecurityGatewayProto,
        access_adapter: AccessGatewayProto,
        user_ensure: UserServiceInsurance,
        logger: CustomLoggerProto,
        config: Configs,
    ) -> None:
        self._security = security_adapter
        self._access = access_adapter
        self._user_ensure = user_ensure
        self._logger = logger
        self._config = config

    async def verify_user_by_token(self, cmd: commands.VerifyUserByTokenCommand) -> UserInfo:
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

        return UserInfo.from_model(user)

    async def authorize(self, cmd: commands.Authorize) -> UserAccessInfo:
        """
        Authorize a user for a specific resource and permission.

        Args:
            cmd (commands.Authorize): Command object containing authorization details.

        Returns:
            UserAccessInfo: Information about the user's access rights.

        Raises:
            Forbidden: If the user is not authorized for the requested resource.
        """
        user_info = await self.verify_user_by_token(
            commands.VerifyUserByTokenCommand(access_token=cmd.access_token)
        )

        if cmd.resource_id is None:
            has_permission = await self._access.check_permission(user_info.role, cmd.resource_type, cmd.permission)
        else:
            has_permission = await self._access.check_object_access(
                user_info.id, user_info.role, cmd.resource_type, cmd.resource_id
            )

        if not has_permission:
            self._logger.error(
                "User is not authorized for resource",
                resource_type=cmd.resource_type,
                resource_id=cmd.resource_id,
            )
            raise Forbidden

        return UserAccessInfo(
            user_id=user_info.id, role=cmd.permission, resource_id=cmd.resource_id, resource_type=cmd.resource_type
        )
