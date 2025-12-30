import uuid
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GetCommentInfo:
    comment_id: uuid.UUID


@dataclass(slots=True, frozen=True)
class ListUserComments:
    user_id: uuid.UUID


@dataclass(slots=True, frozen=True)
class ListHotelComments:
    hotel_id: int
