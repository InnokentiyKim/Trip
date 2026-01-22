from enum import StrEnum


class EnvironmentEnum(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"


class DataAccessEnum(StrEnum):
    ALCHEMY = "alchemy"
    MEMORY = "memory"
    HTTP = "http"
    RABBITMQ = "rabbitmq"
    S3 = "s3"


class GatewayTypeEnum(StrEnum):
    ALCHEMY = DataAccessEnum.ALCHEMY
    MEMORY = DataAccessEnum.MEMORY


class EmailAdapterEnum(StrEnum):
    SMTP = "smtp"
    NAVER = "naver"
    MEMORY = "memory"


class SMSAdapterEnum(StrEnum):
    NAVER = "naver"
    MEMORY = "memory"


class RunModeEnum(StrEnum):
    HTTP = "http"
    AMQP = "amqp"
    FULL = "full"
