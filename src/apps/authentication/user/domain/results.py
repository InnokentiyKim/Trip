from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class OAuthProviderUser:
    id: str
    name: str
    email: str
    picture: str | None = None
