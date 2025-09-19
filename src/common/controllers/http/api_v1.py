from src.apps.hotel.bookings.controllers.v1.http.router import router as booking_router
from fastapi import APIRouter


http_router_v1 = APIRouter(prefix="/api/v1")
http_router_v1.include_router(booking_router)
