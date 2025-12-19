from collections.abc import AsyncIterable, AsyncGenerator

from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig
from aiobotocore.session import get_session
from httpx import AsyncClient, Timeout
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from dishka import Provider, Scope, provide
from dishka import from_context as context
from structlog import BoundLogger, get_logger

from src.common.interfaces import CustomLoggerProto
from src.infrastructure.database.factory import create_database_adapter
from src.config import Configs
from src.infrastructure.logger.adapter import CustomLoggerAdapter
from src.infrastructure.security.adapters.adapter import SecurityAdapter
from src.infrastructure.security.application.interfaces.gateway import SecurityGatewayProto


class ConfigProvider(Provider):
    config = context(provides=Configs, scope=Scope.APP)


class SecurityProvider(Provider):
    scope = Scope.REQUEST

    @provide(provides=SecurityGatewayProto)
    def provide_security_adapter(self, config: Configs) -> SecurityGatewayProto:
        return SecurityAdapter(config)


class LoggingProvider(Provider):
    logger = provide(
        CustomLoggerAdapter,
        provides=CustomLoggerProto,
        scope=Scope.APP,
    )

    @provide(scope=Scope.APP)
    def provide_logger(self, config: Configs) -> BoundLogger:
        """
        Provide a BoundLogger instance configured with the application logger name.

        Args:
            config (Configs): The configuration object containing logger settings.

        Returns:
            BoundLogger: An instance of BoundLogger configured with the application logger name.
        """
        return get_logger(config.logger.app_logger_name)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_db_engine(self, configs: Configs) -> AsyncIterable[AsyncEngine]:
        """Provides a database engine for the application scope.

        Args:
            configs (Configs): The configuration settings.

        Yields:
            AsyncIterable[AsyncEngine]: An asynchronous database engine.
        """
        engine = create_database_adapter(config=configs.database)

        yield engine
        await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def provide_db_session(
        self, engine: AsyncEngine, config: Configs
    ) -> AsyncIterable[AsyncSession]:
        """Provides a database session for the duration of a request.

        Args:
            engine (AsyncEngine): The asynchronous database engine.
            config (Configs): The configuration settings.

        Yields:
            AsyncIterable[AsyncSession]: An asynchronous session for database operations.
        """
        session_config = config.database.session
        async with async_sessionmaker(
            engine, expire_on_commit=session_config.expire_on_commit
        )() as session:
            yield session


class S3Provider(Provider):
    @provide(scope=Scope.APP)
    async def provide_s3_client(self, config: Configs) -> AsyncIterable[AioBaseClient]:
        """Provides an S3 client for the application scope."""
        session = get_session()
        botocore_config = AioConfig(max_pool_connections=config.s3.connection_pool_size)
        async with session.create_client(
            service_name="s3",
            endpoint_url=config.s3.s3_endpoint,
            aws_access_key_id=config.s3.s3_access_key,
            aws_secret_access_key=config.s3.s3_secret_key.get_secret_value(),
            config=botocore_config,
        ) as client:
            yield client


class HttpProvider(Provider):
    @provide(scope=Scope.APP, provides=AsyncClient)
    async def provide_http_adapter(self) -> AsyncGenerator[AsyncClient]:
        async with AsyncClient(
            timeout=Timeout(
                connect=5.0,
                read=10.0,
                write=5.0,
                pool=5.0,
            )
        ) as client:
            yield client


def get_infra_providers() -> list[Provider]:
    """Returns a list of infrastructure providers for dependency injection."""
    return [
        ConfigProvider(),
        DatabaseProvider(),
        LoggingProvider(),
        S3Provider(),
        SecurityProvider(),
        HttpProvider(),
    ]
