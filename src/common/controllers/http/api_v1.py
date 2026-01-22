from fastapi import APIRouter

from src.apps.authentication.session.controllers.v1.http.router import router as auth_router
from src.apps.authentication.user.controllers.http.v1.router import router as user_router
from src.apps.comment.controllers.v1.http.router import router as comment_router
from src.apps.hotel.bookings.controllers.v1.http.router import router as booking_router
from src.apps.hotel.hotels.controllers.v1.http.router import router as hotel_router
from src.apps.hotel.rooms.controllers.v1.http.router import router as room_router

http_router_v1 = APIRouter(prefix="/api/v1")

http_router_v1.include_router(comment_router)
http_router_v1.include_router(hotel_router)
http_router_v1.include_router(room_router)
http_router_v1.include_router(booking_router)
http_router_v1.include_router(auth_router)
http_router_v1.include_router(user_router)
