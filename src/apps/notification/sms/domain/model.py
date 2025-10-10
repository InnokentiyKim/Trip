from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class BaseSMS:
    template: str
    recipients: list[str]

    _EXCLUDED_FIELDS = {"recipients"}

    def __post_init__(self):
        """Validate required non-empty fields."""
        if not self.recipients:
            raise ValueError("Recipients list cannot be empty.")
        if not self.template:
            raise ValueError("Template text cannot be empty.")


@dataclass(frozen=True, kw_only=True, slots=True)
class OTPPasswordResetSMS(BaseSMS):
    template: str = "Your password reset code is {otp_code}. It is valid for {lifetime_minutes} minutes."

    otp_code: str
    lifetime_minutes: int


SMSType = OTPPasswordResetSMS
