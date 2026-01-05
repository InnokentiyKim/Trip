from decimal import Decimal
from pydantic import Field, model_validator
from src.common.controllers.dto.base import BaseRequestDTO


class ListRoomsRequestDTO(BaseRequestDTO):
    price_from: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    price_to: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    services: dict | None = None

    @model_validator(mode='after')
    def validate_price_range(self):
        if self.price_from is not None and self.price_to is not None:
            if self.price_to < self.price_from:
                raise ValueError('price_to должно быть больше price_from')
        return self


class UpdateRoomRequestDTO(BaseRequestDTO):
    name: str | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    quantity: int | None = Field(default=None, ge=1)
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None


class AddRoomRequestDTO(BaseRequestDTO):
    name: str
    price: Decimal = Field(gt=0, decimal_places=2)
    quantity: int | None = Field(default=None, ge=1)
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None
