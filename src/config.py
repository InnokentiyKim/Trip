from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from src.infrastructure.database.postgres.config import DatabaseSettings
from src.common.domain.enums import EnvironmentEnum
from src.apps.hotel.file_object.config import S3Settings
from pydantic import EmailStr
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class GeneralSettings(BaseSettings):
    app_version: str = "1.0.0"
    app_name: str = "backend-hotel-service"
    environment: EnvironmentEnum = EnvironmentEnum.DEV


class SecuritySettings(BaseSettings):
    secret_key: str
    algorithm: str
    token_expire_minutes: int

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = False


class SMTPSettings(BaseSettings):
    smtp_username: str = "HotelsApp"
    smtp_password: SecretStr = SecretStr("app_secret")
    smtp_use_credentials: bool = False
    mail_from: str | EmailStr = "test@yandex.ru"
    mail_from_name: str = "Hotels App"
    smtp_server: str = "smtp.yandex.ru"
    smtp_port: int = 465
    smtp_ssl_tls: bool = True
    smtp_starttls: bool = False


class Configs(BaseSettings):
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    smtp_email: SMTPSettings = Field(default_factory=SMTPSettings)
    s3: S3Settings = Field(default_factory=S3Settings)


def create_configs() -> Configs:
    return Configs()
