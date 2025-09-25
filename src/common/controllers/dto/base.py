from pydantic import BaseModel


class BaseDTO(BaseModel):
    ...


class BaseRequestDTO(BaseDTO):
    ...


class BaseResponseDTO(BaseDTO):
    id: int
