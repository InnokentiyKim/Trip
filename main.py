from fastapi import FastAPI
from src.apps.hotel.bookings.controllers.v1.http.router import router as bookings_router


def create_app() -> FastAPI:
    hotels_app = FastAPI()
    hotels_app.include_router(bookings_router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return hotels_app

if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
