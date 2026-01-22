from pydantic import BaseModel, Field

from src.apps.authentication.session.domain.models import (
    AuthSession,
    OTPCode,
    PasswordResetToken,
)
from src.apps.authentication.user.domain.models import User
from src.apps.authorization.access.domain.models import (
    Permission,
    Role,
    RolePermissions,
)
from src.apps.comment.domain.models import Comment
from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.file_object.domain.models import FileObject
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.rooms.domain.models import Room
from src.config import Configs


class MemoryDatabase(BaseModel):
    def __init__(self, config: Configs):
        super().__init__()
        self.config = config

    # Hotel-related collections
    bookings: set[Booking] = Field(default_factory=set)
    hotels: set[Hotel] = Field(default_factory=set)
    rooms: set[Room] = Field(default_factory=set)
    file_objects: set[FileObject] = Field(default_factory=set)

    # Users/Comments/Auth/Access
    users: set[User] = Field(default_factory=set)
    comments: set[Comment] = Field(default_factory=set)
    permissions: set[Permission] = Field(default_factory=set)
    roles: set[Role] = Field(default_factory=set)
    role_permissions: set[RolePermissions] = Field(default_factory=set)
    auth_sessions: set[AuthSession] = Field(default_factory=set)
    password_reset_tokens: set[PasswordResetToken] = Field(default_factory=set)
    otp_codes: set[OTPCode] = Field(default_factory=set)
