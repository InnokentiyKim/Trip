from enum import StrEnum


class EnvironmentEnum(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"
