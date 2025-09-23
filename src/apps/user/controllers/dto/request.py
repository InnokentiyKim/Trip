from pydantic import EmailStr


class RegisterUserRequestDTO:
    email: EmailStr
    password: str