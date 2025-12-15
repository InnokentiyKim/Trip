from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True, slots=True)
class BaseEmail:
    template_name: str
    subject: str
    recipients: list[str]

    from_email: str
    company_name: str | None
    company_website_url: str | None
    company_logo_url: str | None

    _EXCLUDED_FIELDS = {"recipients", "template_name"}
    _BASE_DIR = Path(__file__).resolve().parent.parent
    _TEMPLATES_DIR = _BASE_DIR / "templates"


@dataclass(frozen=True, kw_only=True, slots=True)
class UserSingUpEmail(BaseEmail):
    template_name: str = ""
    subject: str = ""


@dataclass(frozen=True, kw_only=True, slots=True)
class ConfirmationEmail(BaseEmail):
    template_name: str = ""
    subject: str = ""

    confirmation_link: str
    link_lifetime_minutes: int


@dataclass(frozen=True, kw_only=True, slots=True)
class PasswordResetEmail(BaseEmail):
    template_name: str = ""
    subject: str = ""

    reset_link: str
    link_lifetime_minutes: int


@dataclass(frozen=True, kw_only=True, slots=True)
class MFAVerificationEmail(BaseEmail):
    template_name: str = ""
    subject: str = ""

    verification_code: str
    code_lifetime_minutes: int


EmailType = (
    UserSingUpEmail
    | ConfirmationEmail
    | PasswordResetEmail
    | MFAVerificationEmail
)
