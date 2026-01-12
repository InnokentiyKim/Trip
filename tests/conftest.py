import os
from collections.abc import AsyncGenerator
from enum import StrEnum
from typing import Callable, Any

from dishka import Scope, AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.core.container import DockerContainer
import pytest
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer

from src.apps.authentication.session.domain.models import AuthenticationBase
from src.apps.authentication.user.domain.models import UserBase
from src.apps.authorization.access.domain.models import AuthorizationBase
from src.apps.comment.domain.models import CommentBase
from src.apps.hotel.bookings.domain.models import BookingBase
from src.apps.hotel.hotels.domain.models import HotelBase
from src.apps.hotel.rooms.domain.models import RoomBase
from src.common.controllers.http.api_v1 import http_router_v1
from src.common.domain.enums import DataAccessEnum, EmailAdapterEnum, SMSAdapterEnum
from src.common.exceptions.handlers import general_exception_handler
from src.config import Configs, create_configs
from src.ioc.registry import get_providers
from src.setup.common import create_async_container
from src.common.exceptions.common import BaseError
from tests.fixtures.mocks import MockData


BUCKET_NAME = "images"


def pytest_addoption(parser):
    """Command line options added to pytest."""
    parser.addoption(
        "--no-fake",
        action="store_true",
        default=False,
        help="Use in memory gateway implementations and fake data. Default: False",
    )


def app_configs(config: Configs) -> list[BaseModel]:
    return [
        config.general,
        config.logger,
        config.security,
        config.database,
        config.celery,
        config.smtp_email,
        config.s3,
    ]


def filter_configs_by_data_access(config: Configs, data_access: DataAccessEnum) -> list[BaseModel]:
    return [
        config
        for config in app_configs(config)
        if getattr(config, "data_access", None) == data_access
    ]


def is_postgres_required(config: Configs) -> bool:
    """Determine if Postgres container is required."""
    return bool(filter_configs_by_data_access(config, DataAccessEnum.ALCHEMY))


def is_minio_required(config: Configs) -> bool:
    """Determine if Minio container is required."""
    return bool(filter_configs_by_data_access(config, DataAccessEnum.S3))


def is_memory_database_required(config: Configs) -> bool:
    """Determine if Memory database container is required."""
    return bool(filter_configs_by_data_access(config, DataAccessEnum.MEMORY))


class DockerContainerEnum(StrEnum):
    POSTGRES = "postgres"
    REDIS = "redis"
    MINIO = "minio"


CONTAINERS: dict[DockerContainerEnum, DockerContainer | None] = {
    DockerContainerEnum.POSTGRES: None,
    DockerContainerEnum.REDIS: None,
    DockerContainerEnum.MINIO: None,
}


@pytest.fixture(scope="session", autouse=True)
def stop_docker_containers():
    yield
    for name, docker_container in CONTAINERS.items():
        if CONTAINERS[name] is not None:
            docker_container.stop()
            print(f"Stopped {name} docker container.")
            CONTAINERS[name] = None


@pytest.fixture(scope="module", autouse=True)
def postgres_container(mock_test_config) -> PostgresContainer:
    """Provide a Postgres container for testing."""
    postgres = CONTAINERS[DockerContainerEnum.POSTGRES] or PostgresContainer("postgres:17")

    if is_postgres_required(mock_test_config) and CONTAINERS[DockerContainerEnum.POSTGRES] is None:
        postgres.start()
        os.environ["POSTGRES_USER"] = postgres.username
        os.environ["POSTGRES_PASSWORD"] = postgres.password
        os.environ["POSTGRES_HOST"] = "localhost"
        os.environ["POSTGRES_PORT"] = str(postgres.get_exposed_port(5432))
        os.environ["POSTGRES_DB"] = postgres.dbname

        CONTAINERS[DockerContainerEnum.POSTGRES] = postgres

    if CONTAINERS[DockerContainerEnum.POSTGRES] is not None:
        expire_on_commit = mock_test_config.database.session.expire_on_commit
        mock_test_config.database.__init__()
        mock_test_config.database.session.expire_on_commit = expire_on_commit

    return postgres


@pytest.fixture(scope="module", autouse=True)
def minio_container(mock_test_config) -> MinioContainer:
    """Provide a Minio container for testing."""
    minio = CONTAINERS[DockerContainerEnum.MINIO] or MinioContainer()

    if is_minio_required(mock_test_config) and CONTAINERS[DockerContainerEnum.MINIO] is None:
        minio.start()
        minio_config = minio.get_config()
        os.environ["S3_ENDPOINT"] = "http://" + minio_config["endpoint"]
        os.environ["S3_BUCKET"] = BUCKET_NAME
        os.environ["S3_ACCESS_KEY"] = minio_config["access_key"]
        os.environ["S3_SECRET_KEY"] = minio_config["secret_key"]
        client = minio.get_client()
        client.make_bucket(BUCKET_NAME)

        CONTAINERS[DockerContainerEnum.MINIO] = minio

    if CONTAINERS[DockerContainerEnum.MINIO] is not None:
        mock_test_config.s3.__init__()

    return minio


@pytest.fixture(scope="session")
def default_config() -> Configs:
    """Fixture that provides the default configuration for tests and run test dependencies."""
    return create_configs()


@pytest.fixture(scope="module")
def default_test_config(default_config, request) -> Configs:
    """Fixture that provides configuration for tests."""
    new_config = default_config.model_copy(deep=True)

    is_fake = not request.config.getoption("--no-fake")
    if is_fake:
        for app_config in app_configs(new_config):
            if hasattr(app_config, "gateway"):
                app_config.gateway = DataAccessEnum.MEMORY
            if hasattr(app_config, "view"):
                app_config.view = DataAccessEnum.MEMORY

    for app_config in app_configs(new_config):
        # Clear default fake data to not conflict with test fake data.
        if hasattr(app_config, "fake_data"):
            app_config.fake_data = []

    # Notification
    new_config.general.email_adapter = EmailAdapterEnum.MEMORY
    new_config.general.sms_adapter = SMSAdapterEnum.MEMORY

    # For useful testing purpose
    new_config.database.session.expire_on_commit = False

    # Memory database
    new_config.memory_database.life_scope = Scope.APP

    return new_config


@pytest.fixture(scope="module")
def mock_test_config(default_test_config) -> Configs:
    """
    Set up a mock config for testing.

    Override this fixture if you need to change the default config for testing.
    """
    return default_test_config


# Type aliases for fixture factories
type SaveInstances = Callable[[MockData[Any]], Any]


@pytest.fixture
def save_instances(request_container) -> SaveInstances:
    async def _task(mock_data: MockData[Any]):
        gateway = await request_container.get(dependency_type=mock_data.gateway_proto)
        await mock_data.save_by_gateway(gateway)

    async def _mock_data(*mocked_data_list):
        for mocked_data in mocked_data_list:
            await _task(mocked_data)

    return _mock_data


@pytest.fixture
async def app_container(mock_test_config) -> AsyncGenerator[AsyncContainer]:
    providers = [*get_providers()]
    container = create_async_container(providers, config=mock_test_config)
    yield container
    await container.close()


@pytest.fixture
async def request_container(app_container) -> AsyncGenerator[AsyncContainer]:
    async with app_container() as request_container:
        yield request_container


@pytest.fixture
def get_test_app(app_container) -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(BaseError, general_exception_handler)
    app.include_router(http_router_v1)
    setup_dishka(container=app_container, app=app)
    return app


@pytest.fixture
async def sqlalchemy_engine(app_container) -> AsyncGenerator[AsyncEngine]:
    async with app_container() as request_container:
        engine = await request_container.get(dependency_type=AsyncEngine)
        yield engine


@pytest.fixture
async def http_client(get_test_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=get_test_app), base_url="http://test") as ac:
        yield ac


async def init_postgres_tables(sqlalchemy_engine: AsyncEngine) -> None:
    """Initialize Postgres tables for testing."""

    base_metadata = {
        AuthenticationBase.metadata,
        AuthorizationBase.metadata,
        HotelBase.metadata,
        BookingBase.metadata,
        RoomBase.metadata,
        UserBase.metadata,
        CommentBase.metadata,
    }

    async with sqlalchemy_engine.begin() as conn:
        for metadata in base_metadata:
            await conn.run_sync(metadata.drop_all)
            await conn.run_sync(metadata.create_all)


async def init_memory_database(app_container: AsyncContainer, mock_test_config: Configs):
    async with app_container() as request_container:
        memory_database = await request_container.get()