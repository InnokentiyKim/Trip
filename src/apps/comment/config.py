from enum import StrEnum

from pydantic import BaseModel

from src.apps.comment.domain.models import Comment
from src.common.domain.enums import DataAccessEnum


class CommentGatewayEnum(StrEnum):
    ALCHEMY = DataAccessEnum.ALCHEMY
    MEMORY = DataAccessEnum.MEMORY


class CommentConfig(BaseModel):
    gateway: CommentGatewayEnum = CommentGatewayEnum.ALCHEMY
    fake_data: list[Comment] = []
