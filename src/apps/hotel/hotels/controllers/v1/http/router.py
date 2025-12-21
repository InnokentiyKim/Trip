from fastapi import APIRouter, Query

from src.apps.hotel.hotels.application.exceptions import HotelNotFoundException
from src.apps.hotel.hotels.controllers.v1.dto.request import (
    ListHotelsRequestDTO,
    UpdateHotelRequestDTO,
)
from typing import Annotated
from src.apps.hotel.hotels.domain import commands as hotel_commands
from src.apps.authentication.user.domain import commands as user_commands
from src.apps.authentication.user.application.exceptions import Unauthorized, Forbidden
from src.apps.hotel.hotels.controllers.v1.dto.request import CreateHotelRequestDTO
from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header
from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.hotels.controllers.v1.dto.response import (
    GetHotelsResponseDTO,
    CreateHotelResponseDTO,
    UpdateHotelResponseDTO,
    UploadHotelImageResponseDTO,
)
from src.apps.authentication.user.application.service import UserService
from dishka.integrations.fastapi import FromDishka, inject


router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)


@router.get(
    "",
    responses=generate_responses(
        Unauthorized,
    ),
)
@inject
async def get_hotels(
    filter_query: Annotated[ListHotelsRequestDTO, Query()],
    hotel_service: FromDishka[HotelService],
) -> list[GetHotelsResponseDTO]:
    cmd = hotel_commands.ListHotelsCommand(
        location=filter_query.location, services=filter_query.services, rooms_quantity=filter_query.rooms_quantity
    )
    hotels = await hotel_service.list_hotels(cmd)
    return [GetHotelsResponseDTO.model_validate(hotel) for hotel in hotels]


@router.get(
    "/{hotel_id}",
    responses=generate_responses(
        Unauthorized,
    ),
)
@inject
async def get_hotel(
    hotel_id: int,
    hotel_service: FromDishka[HotelService],
) -> GetHotelsResponseDTO:
    hotel = await hotel_service.get_hotel(
        hotel_commands.GetHotelCommand(hotel_id=hotel_id)
    )
    return GetHotelsResponseDTO.model_validate(hotel, from_attributes=True)


@router.post(
    "",
    responses=generate_responses(
        Unauthorized,
    ),
)
@inject
async def create_hotel(
    dto: CreateHotelRequestDTO,
    user_service: FromDishka[UserService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header,
) -> CreateHotelResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(access_token=token)
    )
    cmd = hotel_commands.CreateHotelCommand(
        name=dto.name,
        location=dto.location,
        rooms_quantity=dto.rooms_quantity,
        owner=user.id,
        is_active=dto.is_active,
        services=dto.services,
        image_id=dto.image_id,
    )
    hotel_id = await hotel_service.create_hotel(cmd)
    return CreateHotelResponseDTO(id=hotel_id)


@router.post(
    "/{hotel_id}/upload-image",
    responses=generate_responses(
        Unauthorized,
        HotelNotFoundException,
        Forbidden,
    ),
)
@inject
async def upload_hotel_image(
    hotel_id: int,
    user_service: FromDishka[UserService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header,
) -> UploadHotelImageResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(access_token=token)
    )
    hotel = await hotel_service.get_hotel(
        hotel_commands.GetHotelCommand(hotel_id=hotel_id)
    )
    url = ""
    return UploadHotelImageResponseDTO(url=url, hotel_id=hotel_id)


@router.patch(
    "",
    responses=generate_responses(
        Unauthorized,
    ),
)
@inject
async def update_hotel(
    dto: UpdateHotelRequestDTO,
    user_service: FromDishka[UserService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header,
) -> UpdateHotelResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(access_token=token)
    )
    cmd = hotel_commands.UpdateHotelCommand(
        hotel_id=dto.hotel_id,
        name=dto.name,
        location=dto.location,
        rooms_quantity=dto.rooms_quantity,
        owner=user.id,
        is_active=dto.is_active,
        services=dto.services,
        image_id=dto.image_id,
    )
    hotel_id = await hotel_service.update_hotel(cmd)
    return UpdateHotelResponseDTO(id=hotel_id)
