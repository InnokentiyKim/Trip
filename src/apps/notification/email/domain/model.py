from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class BaseEmail:
    template_name: str
    subject: str
    to_email: str
    from_email: str


@dataclass(frozen=True, kw_only=True, slots=True)
class UserSingUpEmail(BaseEmail):
    template_name: str = ""
    subject: str = ""


EmailType = (
    UserSingUpEmail
    | BaseEmail
)
