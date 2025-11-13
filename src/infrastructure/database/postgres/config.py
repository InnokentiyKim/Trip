from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings


class SqlEngineConfig(BaseModel):
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


class SqlSessionConfig(BaseModel):
    # Set to False for async sessions (SQLAlchemy 2.0 recommendation)
    # Reason: Cannot lazy load expired attributes after commit in async context
    # See: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
    expire_on_commit: bool = False


class DatabaseSettings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: SecretStr = SecretStr("postgres")
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "hotels_db"

    engine: SqlEngineConfig = Field(default_factory=SqlEngineConfig)
    session: SqlSessionConfig = Field(default_factory=SqlSessionConfig)

    @property
    def db_url(self) -> str:
        """
        Constructs the full database connection URL for SQLAlchemy with the asyncpg driver.

        Returns:
            str: A fully formatted database URL string
        """
        db_params = {
            "user": self.postgres_user,
            "password": self.postgres_password.get_secret_value(),
            "host": self.postgres_host,
            "port": self.postgres_port,
            "db": self.postgres_db,
        }
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(**db_params)
