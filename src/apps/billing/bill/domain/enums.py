from enum import Enum


class CurrencyEnum(str, Enum):
    USD = "USD"
    RUB = "RUB"


class BillingStatusEnum(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"
