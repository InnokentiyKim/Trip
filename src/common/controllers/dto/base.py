from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel): ...


class BaseRequestDTO(BaseDTO): ...


class BaseResponseDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int | UUID
