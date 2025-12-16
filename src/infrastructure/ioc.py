from typing import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from dishka import Provider, Scope, provide
from dishka import from_context as context

from src.infrastructure.database.factory import create_database_adapter
from src.config import Configs
from src.infrastructure.security.adapters.adapter import SecurityAdapter
from src.infrastructure.security.application.interfaces.gateway import SecurityGatewayProto


class ConfigProvider(Provider):
    config = context(provides=Configs, scope=Scope.APP)


class SecurityProvider(Provider):
    scope = Scope.REQUEST

    @provide(provides=SecurityGatewayProto)
    def provide_security_adapter(self, config: Configs) -> SecurityGatewayProto:
        return SecurityAdapter(config)


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


def get_infra_providers() -> list[Provider]:
    """Returns a list of infrastructure providers for dependency injection."""
    return [
        ConfigProvider(),
        SecurityProvider(),
        DatabaseProvider(),
    ]
