from fastapi import FastAPI


def create_app() -> FastAPI:
    hotels_app = FastAPI()

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return hotels_app

if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
