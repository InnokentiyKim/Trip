from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from src.infrastructure.database.postgres.config import DatabaseSettings
from src.common.domain.enums import EnvironmentEnum
from src.apps.hotel.file_object.config import S3Settings
from pydantic import EmailStr
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class CustomBaseSettings(BaseSettings):
    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = False


class GeneralSettings(CustomBaseSettings):
    app_version: str = "1.0.0"
    app_name: str = "backend-hotel-service"
    environment: EnvironmentEnum = EnvironmentEnum.DEV


class SecuritySettings(CustomBaseSettings):
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 1440  # 1 day


class SMTPSettings(CustomBaseSettings):
    smtp_username: str = "HotelsApp"
    smtp_password: SecretStr = SecretStr("app_secret")
    smtp_use_credentials: bool = False
    mail_from: str | EmailStr = "HotelsApp@yandex.ru"
    mail_from_name: str = "Hotels App"
    smtp_server: str = "smtp.yandex.ru"
    smtp_port: int = 465
    smtp_ssl_tls: bool = True
    smtp_starttls: bool = False


class CelerySettings(CustomBaseSettings):
    # Celery broker and backend URLs
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"
    # Worker settings
    worker_concurrency: int = 4
    worker_prefetch_multiplier: int = 1
    worker_max_tasks_per_child: int = 1000
    # Timeouts
    task_time_limit: int = 300
    task_soft_time_limit: int = 240
    # Results
    result_expires: int = 3600


class LoggerSettings(BaseSettings):
    log_level: str = "DEBUG"
    app_logger_name: str = "hotels_backend.service_logs"
    api_logger_name: str = "hotels_backend.api_logs"


class Configs(BaseSettings):
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    smtp_email: SMTPSettings = Field(default_factory=SMTPSettings)
    s3: S3Settings = Field(default_factory=S3Settings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    logger: LoggerSettings = Field(default_factory=LoggerSettings)


def create_configs() -> Configs:
    return Configs()
