from pydantic_settings import BaseSettings
from pydantic import Field

from common.application.enums import EnvironmentEnum


class GeneralSettings(BaseSettings):
    app_version: str = "0.0.1"
    app_name: str = "backend-hotel-service"
    environment: EnvironmentEnum = EnvironmentEnum.LOCAL


class DatabaseSettings(BaseSettings):
    host: str
    port: int
    user: str
    name: str
    password: str

    class Config:
        env_prefix = "DB_"
        env_file = ".env"
        case_sensitive = False


class SecuritySettings(BaseSettings):
    secret_key: str
    algorithm: str
    token_expire_minutes: int

    class Config:
        env_file = ".env"
        case_sensitive = False


class Configs(BaseSettings):
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)


def create_configs() -> Configs:
    return Configs()
