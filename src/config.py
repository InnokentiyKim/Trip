from pathlib import Path

from pydantic import BaseModel, EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings

from src.common.domain.enums import EmailAdapterEnum, EnvironmentEnum, SMSAdapterEnum
from src.infrastructure.database.memory.config import MemoryDatabaseSettings
from src.infrastructure.database.postgres.config import DatabaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class CORSConfig(BaseModel):
    """CORS configuration for the FastAPI application."""

    allow_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://127.0.0.1:3000",
        ],
        description="List of allowed origins for CORS",
    )
    allow_credentials: bool = Field(
        default=True,
        description="Whether to allow credentials (cookies, authorization headers)",
    )
    allow_methods: list[str] = Field(
        default=["*"],
        description="List of allowed HTTP methods",
    )
    allow_headers: list[str] = Field(
        default=["*"],
        description="List of allowed HTTP headers",
    )
    expose_headers: list[str] = Field(
        default=[
            "Content-Length",
            "Content-Type",
            "Content-Disposition",
            "Content-Range",
            "X-Content-Type-Options",
            "X-Video-Rotation",
            "X-Thumbnail-Extraction-Time-Ms",
            "X-Thumbnail-Bytes-Downloaded",
            "X-Thumbnail-Savings-Percentage",
            "X-Thumbnail-S3-Requests",
            "X-Thumbnail-Frame-Number",
            "X-Thumbnail-Size-Bytes",
        ],
        description="Headers exposed to the browser for cross-origin requests",
    )


class CustomBaseSettings(BaseSettings):
    """Custom base settings to configure environment file and case sensitivity."""

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = False
        extra = "ignore"


class GeneralSettings(CustomBaseSettings):
    """General application configuration settings."""

    app_version: str = "1.0.0"
    app_name: str = "hotel-service-backend"
    environment: EnvironmentEnum = EnvironmentEnum.DEV
    log_level: str = "DEBUG"
    cors: CORSConfig = Field(default_factory=CORSConfig)

    email_adapter: EmailAdapterEnum = EmailAdapterEnum.SMTP
    sms_adapter: SMSAdapterEnum = SMSAdapterEnum.NAVER
    company_name: str = "HOTELS"
    website_url: str = "http://localhost:3000"
    support_email: str = "support@hotels.app"
    logo_url: str = ""


class SecuritySettings(CustomBaseSettings):
    """Security configuration settings."""

    secret_key: SecretStr = SecretStr("some_secret_key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 1440  # 1 day
    jwt_key_id: str = "primary"


class AuthenticationSettings(CustomBaseSettings):
    """Authentication configuration settings."""

    reset_password_token_lifetime_minutes: int = 5
    otp_lifetime_minutes: int = 3
    otp_max_attempts: int = 5
    mfa_token_lifetime_minutes: int = 3
    max_login_attempts: int = 5
    bypass_otp_code_enabled: bool = False
    bypass_otp_code: str = "000000"


class SMTPSettings(CustomBaseSettings):
    """SMTP email configuration settings."""

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
    """Celery configuration settings."""

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


class S3Settings(BaseSettings):
    """S3 configuration settings."""

    bucket_name: str = "hotel-app-bucket"
    sample_files_prefix: str = "sample"
    s3_endpoint: str = "http://localhost:9000"
    s3_endpoint_public: str = "http://localhost:9000"
    s3_access_key: str = "minio-user"
    s3_secret_key: SecretStr = SecretStr("minio-password")
    connection_pool_size: int = 30
    s3_file_download_size: int = 2097152


class LoggerSettings(BaseSettings):
    """Logger configuration settings."""

    log_level: str = "DEBUG"
    app_logger_name: str = "hotels_backend.service_logs"
    api_logger_name: str = "hotels_backend.api_logs"


class Configs(BaseSettings):
    """Application configuration settings."""

    general: GeneralSettings = Field(default_factory=GeneralSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    memory_database: MemoryDatabaseSettings = Field(default_factory=MemoryDatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    auth: AuthenticationSettings = Field(default_factory=AuthenticationSettings)
    smtp_email: SMTPSettings = Field(default_factory=SMTPSettings)
    s3: S3Settings = Field(default_factory=S3Settings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    logger: LoggerSettings = Field(default_factory=LoggerSettings)


def create_configs() -> Configs:
    """Create and return the application configuration."""
    return Configs()
