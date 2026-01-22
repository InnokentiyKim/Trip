from enum import StrEnum


class CurrencyEnum(StrEnum):
    USD = "USD"
    RUB = "RUB"


class BillingStatusEnum(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"
