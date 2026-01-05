from fastapi import APIRouter, Query

from src.apps.authorization.access.application.service import AccessService
from src.apps.authorization.access.domain.commands import Authorize
from src.apps.authorization.access.domain.enums import HotelPermissionEnum, ResourceTypeEnum
from src.apps.hotel.hotels.application.exceptions import HotelNotFoundException, HotelAlreadyExistsException
from src.apps.hotel.hotels.controllers.v1.dto.request import (
    ListHotelsRequestDTO,
    UpdateHotelRequestDTO,
)
from typing import Annotated
from src.apps.hotel.hotels.domain import commands as hotel_commands
from src.apps.authentication.user.application.exceptions import Unauthorized, UserNotFoundException
from src.apps.authorization.access.domain.exceptions import Forbidden
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
from dishka.integrations.fastapi import FromDishka, inject


router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)
# TODO: Add all hotel_id to request DTO's UUID fields

@router.get(
    "",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
    ),
)
@inject
async def get_hotels(
    filter_query: Annotated[ListHotelsRequestDTO, Query()],
    hotel_service: FromDishka[HotelService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> list[GetHotelsResponseDTO]:
    # Authorize user
    await access_service.authorize(
        Authorize(
            access_token=token,
            permission=HotelPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.HOTEL,
        )
    )

    cmd = hotel_commands.ListHotelsCommand(
        location=filter_query.location, services=filter_query.services, rooms_quantity=filter_query.rooms_quantity
    )
    hotels = await hotel_service.list_hotels(cmd)
    return [GetHotelsResponseDTO.model_validate(hotel) for hotel in hotels]


@router.get(
    "/{hotel_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
        HotelNotFoundException,
    ),
)
@inject
async def get_hotel(
    hotel_id: int,
    hotel_service: FromDishka[HotelService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> GetHotelsResponseDTO:
    # Authorize user
    await access_service.authorize(
        Authorize(
            access_token=token,
            permission=HotelPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.HOTEL,
        )
    )

    hotel = await hotel_service.get_hotel(
        hotel_commands.GetHotelCommand(hotel_id=hotel_id)
    )
    return GetHotelsResponseDTO.model_validate(hotel, from_attributes=True)


@router.post(
    "",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
        HotelAlreadyExistsException,
    ),
)
@inject
async def create_hotel(
    dto: CreateHotelRequestDTO,
    access_service: FromDishka[AccessService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header,
) -> CreateHotelResponseDTO:
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=HotelPermissionEnum.CAN_CREATE,
            resource_type=ResourceTypeEnum.HOTEL,
        )
    )

    cmd = hotel_commands.CreateHotelCommand(
        name=dto.name,
        location=dto.location,
        rooms_quantity=dto.rooms_quantity,
        owner=authorization_info.user_id,
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
        Forbidden,
        UserNotFoundException,
        HotelNotFoundException,
    ),
)
@inject
async def upload_hotel_image(
    hotel_id: int,
    access_service: FromDishka[AccessService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header,
) -> UploadHotelImageResponseDTO:
    # Authorize user
    await access_service.authorize(
        Authorize(
            access_token=token,
            permission=HotelPermissionEnum.CAN_EDIT,
            resource_type=ResourceTypeEnum.HOTEL,
            resource_id=hotel_id,
        )
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
        Forbidden,
        UserNotFoundException,
        HotelNotFoundException,
    ),
)
@inject
async def update_hotel(
    dto: UpdateHotelRequestDTO,
    access_service: FromDishka[AccessService],
    hotel_service: FromDishka[HotelService],
    token: str = auth_header,
) -> UpdateHotelResponseDTO:
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=HotelPermissionEnum.CAN_EDIT,
            resource_type=ResourceTypeEnum.HOTEL,
            resource_id=dto.hotel_id,
        )
    )

    cmd = hotel_commands.UpdateHotelCommand(
        hotel_id=dto.hotel_id,
        name=dto.name,
        location=dto.location,
        rooms_quantity=dto.rooms_quantity,
        owner=authorization_info.user_id,
        is_active=dto.is_active,
        services=dto.services,
        image_id=dto.image_id,
    )
    hotel_id = await hotel_service.update_hotel(cmd)
    return UpdateHotelResponseDTO(id=hotel_id)
