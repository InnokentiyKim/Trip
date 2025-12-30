from uuid import UUID

from src.apps.authentication.user.application.ensure import UserServiceEnsurance
from src.apps.comment.application.interfaces.gateway import CommentGatewayProto
from src.apps.comment.domain.commands import AddCommentCommand, UpdateCommentInfoCommand, DeleteCommentCommand
from src.apps.comment.domain.fetches import ListUserComments, ListHotelComments, GetCommentInfo
from src.apps.comment.domain.excepitions import CommentNotFoundException
from src.apps.comment.domain.models import Comment
from src.apps.comment.domain.results import CommentInfo
from src.apps.hotel.hotels.application.ensure import HotelServiceEnsurance
from src.common.application.service import ServiceBase
from src.common.interfaces import CustomLoggerProto


class CommentService(ServiceBase):
    def __init__(
        self,
        comment_adapter: CommentGatewayProto,
        hotel_ensure: HotelServiceEnsurance,
        user_ensure: UserServiceEnsurance,
        logger: CustomLoggerProto,
    ) -> None:
        self._comment = comment_adapter
        self._hotel_ensure = hotel_ensure
        self._user_ensure = user_ensure
        self._logger = logger

    async def add_comment(self, cmd: AddCommentCommand) -> UUID:
        hotel = await self._hotel_ensure.hotel_exists(cmd.hotel_id)
        user = await self._user_ensure.user_exists(cmd.user_id)

        comment = Comment(
            hotel_id=hotel.id,
            user_id=user.id,
            content=cmd.content,
            rating=cmd.rating,
        )
        await self._comment.add(comment)
        self._logger.info(f"New comment added", id=comment.id, hotel_id=hotel.id, user_id=user.id)

        return comment.id

    async def get_comment(self, fetch: GetCommentInfo) -> CommentInfo:
        comment = await self._comment.get_comment_by_id(fetch.comment_id)

        if comment is None:
            self._logger.info("Comment not found", comment_id=fetch.comment_id)
            raise CommentNotFoundException

        return CommentInfo.from_model(comment)

    async def list_user_comments(self, fetch: ListUserComments) -> list[CommentInfo]:
        user = await self._user_ensure.user_exists(fetch.user_id)
        comments = await self._comment.get_comments_by_user_id(user.id)

        return [CommentInfo.from_model(comment) for comment in comments]

    async def list_hotel_comments(self, fetch: ListHotelComments) -> list[CommentInfo]:
        hotel = await self._hotel_ensure.hotel_exists(fetch.hotel_id)
        comments = await self._comment.get_comments_by_hotel_id(hotel.id)

        return [CommentInfo.from_model(comment) for comment in comments]

    async def update_comment_info(self, cmd: UpdateCommentInfoCommand) -> None:
        comment = await self._comment.get_comment_by_id(cmd.comment_id)

        if comment is None:
            self._logger.info("Comment not found", comment_id=cmd.comment_id)
            raise CommentNotFoundException

        updating_params = cmd.model_dump(
            exclude={"comment_id"}, exclude_unset=True
        )
        for key, value in updating_params.items():
            setattr(comment, key, value)

        await self._comment.update_comment(comment, **updating_params)
        self._logger.info("Comment info updated", comment_id=comment.id)

    async def delete_comment(self, cmd: DeleteCommentCommand) -> None:
        comment = await self._comment.get_comment_by_id(cmd.comment_id)

        if comment is None:
            self._logger.info("Comment not found", comment_id=cmd.comment_id)
            raise CommentNotFoundException

        await self._comment.delete_comment(comment)
        self._logger.info("Comment deleted", comment_id=comment.id)
