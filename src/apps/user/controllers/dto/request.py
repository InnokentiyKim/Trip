from pydantic import EmailStr


class AuthUserRequestDTO:
    email: EmailStr
    password: str
