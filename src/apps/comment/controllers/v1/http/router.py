from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query, status

from src.apps.authentication.user.application.exceptions import (
    Unauthorized,
    UserNotFoundError,
)
from src.apps.authorization.access.application.service import AccessService
from src.apps.authorization.access.domain.commands import Authorize
from src.apps.authorization.access.domain.enums import (
    CommentPermissionEnum,
    ResourceTypeEnum,
)
from src.apps.authorization.access.domain.exceptions import Forbidden
from src.apps.comment.application.service import CommentService
from src.apps.comment.controllers.v1.dto import request, response
from src.apps.comment.controllers.v1.dto.request import ListCommentsRequestDTO
from src.apps.comment.domain import commands, fetches
from src.apps.comment.domain.excepitions import CommentNotFoundError
from src.apps.hotel.hotels.application.exceptions import HotelNotFoundError
from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header

router = APIRouter(
    prefix="/hotels/comments",
    tags=["comments"],
)


@router.get(
    "/{comment_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        CommentNotFoundError,
    ),
)
@inject
async def get_comment(
    comment_id: UUID,
    comment_service: FromDishka[CommentService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> response.CommentInfoResponseDTO:
    """Get comment by ID."""
    # Authorize user
    await access_service.authorize(
        Authorize(
            access_token=token,
            permission=CommentPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.COMMENT,
            resource_id=comment_id,
        )
    )

    comment_info = await comment_service.get_comment(fetch=fetches.GetCommentInfo(comment_id=comment_id))

    return response.CommentInfoResponseDTO.from_model(comment_info)


@router.get(
    "",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        HotelNotFoundError,
    ),
)
@inject
async def list_comments(
    filter_query: Annotated[ListCommentsRequestDTO, Query()],
    comment_service: FromDishka[CommentService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> list[response.CommentInfoResponseDTO]:
    """List comments for a specific hotel."""
    # Authorize user
    await access_service.authorize(
        Authorize(
            access_token=token,
            permission=CommentPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.COMMENT,
        )
    )

    comments_info = await comment_service.list_hotel_comments(
        fetch=fetches.ListHotelComments(hotel_id=filter_query.hotel_id)
    )

    return [response.CommentInfoResponseDTO.from_model(comment) for comment in comments_info]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        HotelNotFoundError,
    ),
)
@inject
async def add_comment(
    dto: request.AddCommentRequestDTO,
    comment_service: FromDishka[CommentService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> response.AddCommentResponseDTO:
    """Add a new comment to a hotel."""
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=CommentPermissionEnum.CAN_CREATE,
            resource_type=ResourceTypeEnum.COMMENT,
        )
    )

    comment_id = await comment_service.add_comment(
        cmd=commands.AddCommentCommand(
            user_id=authorization_info.user_id,
            hotel_id=dto.hotel_id,
            content=dto.content,
            rating=dto.rating,
        )
    )

    return response.AddCommentResponseDTO(id=comment_id)


@router.patch(
    "/{comment_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        CommentNotFoundError,
    ),
)
@inject
async def update_comment(
    comment_id: UUID,
    dto: request.UpdateCommentRequestDTO,
    comment_service: FromDishka[CommentService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> response.UpdateCommentResponseDTO:
    """Update an existing comment."""
    # Authorize user
    await access_service.authorize(
        Authorize(
            access_token=token,
            permission=CommentPermissionEnum.CAN_EDIT,
            resource_type=ResourceTypeEnum.COMMENT,
            resource_id=comment_id,
        )
    )

    await comment_service.update_comment_info(
        cmd=commands.UpdateCommentInfoCommand(
            comment_id=comment_id,
            content=dto.content,
            rating=dto.rating,
        )
    )

    return response.UpdateCommentResponseDTO(id=comment_id)


@router.delete(
    "/{comment_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        CommentNotFoundError,
    ),
)
@inject
async def delete_comment(
    comment_id: UUID,
    comment_service: FromDishka[CommentService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> response.DeleteCommentResponseDTO:
    """Delete a comment by ID."""
    # Authorize user
    await access_service.authorize(
        Authorize(
            access_token=token,
            permission=CommentPermissionEnum.CAN_DELETE,
            resource_type=ResourceTypeEnum.COMMENT,
            resource_id=comment_id,
        )
    )

    await comment_service.delete_comment(
        cmd=commands.DeleteCommentCommand(
            comment_id=comment_id,
        )
    )

    return response.DeleteCommentResponseDTO(id=comment_id)
