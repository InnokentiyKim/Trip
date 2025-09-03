from pydantic_settings import BaseSettings
from enum import StrEnum
from pydantic import Field


class EnvironmentEnum(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"


class GeneralSettings(BaseSettings):
    app_version: str = "0.0.1"
    app_name: str = "backend-hotel-service"
    environment: EnvironmentEnum = EnvironmentEnum.LOCAL


class Configs(BaseSettings):
    general: GeneralSettings = Field(default_factory=GeneralSettings)
