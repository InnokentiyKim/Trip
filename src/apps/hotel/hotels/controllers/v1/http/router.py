from fastapi import APIRouter

from apps.hotel.hotels.application.commands import CreateHotelCommand
from src.apps.authentication.application.exceptions import Unauthorized
from src.apps.hotel.hotels.controllers.v1.dto.request import CreateHotelRequestDTO
from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header
from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.hotels.controllers.v1.dto.response import GetHotelsResponseDTO, CreateHotelResponseDTO
from src.apps.user.application.service import UserService
from dishka.integrations.fastapi import FromDishka, inject


router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)


@router.get(
    "",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def get_hotels(
    user_service: FromDishka[UserService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header
) -> list[GetHotelsResponseDTO]:
    user = await user_service.verify_user_by_token(token)
    hotels = await hotel_service.list_hotels()
    return [GetHotelsResponseDTO.from_model(hotel) for hotel in hotels]


@router.get(
    "/{hotel_id}",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def get_hotel(
    hotel_id: int,
    user_service: FromDishka[UserService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header
) -> GetHotelsResponseDTO:
    user = await user_service.verify_user_by_token(token)
    hotel = await hotel_service.get_hotel(hotel_id)
    return GetHotelsResponseDTO.from_model(hotel)


@router.post(
    "",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def create_hotel(
    dto: CreateHotelRequestDTO,
    user_service: FromDishka[UserService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header,
) -> CreateHotelResponseDTO:
    user = await user_service.verify_user_by_token(token)
    cmd = CreateHotelCommand.from_model(dto)
    hotel_id = await hotel_service.create_hotel(cmd)
    return  CreateHotelResponseDTO(id=hotel_id)
