from dataclasses import asdict, dataclass
from pathlib import Path
from typing import ClassVar

from jinja2 import Environment, FileSystemLoader


@dataclass(frozen=True, kw_only=True, slots=True)
class BaseEmail:
    template_name: str
    subject: str
    recipients: list[str]

    from_email: str
    additional_data: dict[str, str] | None = None
    company_name: str | None = None
    company_website_url: str | None = None
    company_logo_url: str | None = None

    _EXCLUDED_FIELDS = {"recipients", "template_name"}
    _BASE_DIR = Path(__file__).resolve().parent.parent
    _TEMPLATES_DIR = _BASE_DIR / "templates"

    # Initialize Jinja2 environment
    _jinja_env: ClassVar[Environment] = Environment(
        loader=FileSystemLoader(_TEMPLATES_DIR),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def __post_init__(self) -> None:
        """Validate required non-empty fields."""
        if not self.template_name:
            raise ValueError("Template name cannot be empty.")
        if not self.recipients:
            raise ValueError("Recipients list cannot be empty.")
        if not self.template_name:
            raise ValueError("Subject cannot be empty.")

    @property
    def _template_context(self) -> dict[str, str | int]:
        """
        Generates a context dictionary for Jinja2 template rendering.

        It is essential to provide a custom context for each email template
        but exclude base fields like recipients and template_name.

        Returns:
            dict: The context as dictionary.
        """
        all_instance_fields = asdict(self)

        # Create the context by including the instance fields
        return {key: value for key, value in all_instance_fields.items() if key not in self._EXCLUDED_FIELDS}

    @property
    def rendered_content(self) -> str:
        """
        Render the email template with the context.

        Returns:
            str: The rendered template as a string.
        """
        template = self._jinja_env.get_template(self.template_name)
        return template.render(**self._template_context)


@dataclass(frozen=True, kw_only=True, slots=True)
class UserSingUpEmail(BaseEmail):
    template_name: str = ""
    subject: str = ""


@dataclass(frozen=True, kw_only=True, slots=True)
class ConfirmationEmail(BaseEmail):
    template_name: str = ""
    subject: str = ""

    confirmation_link: str = ""
    link_lifetime_minutes: int | None = None


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


EmailType = UserSingUpEmail | ConfirmationEmail | PasswordResetEmail | MFAVerificationEmail
