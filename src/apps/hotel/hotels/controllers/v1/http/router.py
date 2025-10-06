from fastapi import APIRouter, Request
from src.apps.hotel.hotels.adapters.adapter import HotelAdapter
from src.apps.hotel.hotels.application.service import HotelService
from src.apps.hotel.hotels.controllers.v1.dto.response import GetHotelsResponseDTO
from infrastructure.security.adapters.adapter import SecurityAdapter
from src.apps.user.adapters.adapter import UserAdapter
from src.apps.user.application.service import UserService


router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)


@router.get("")
async def get_hotels(request: Request) -> list[GetHotelsResponseDTO]:
    user_service = UserService(UserAdapter(), SecurityAdapter())
    service = HotelService(HotelAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user = await user_service.verify_user_by_token(token)
    hotels = await service.get_hotels()
    return [GetHotelsResponseDTO.from_model(hotel) for hotel in hotels]

@router.get("/{hotel_id}")
async def get_hotel(request: Request, hotel_id: int) -> GetHotelsResponseDTO:
    user_service = UserService(UserAdapter(), SecurityAdapter())
    service = HotelService(HotelAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user = await user_service.verify_user_by_token(token)
    hotel = await service.get_hotel(hotel_id)
    return GetHotelsResponseDTO.from_model(hotel)
