import asyncio

from src.ioc_registry import get_providers
from dishka import make_async_container
from src.setup.fastapi_app import create_fastapi_app
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_ioc
import uvicorn


async def _start_app(port: int) -> None:

    container = make_async_container(*get_providers())

    try:
        fastapi_app = create_fastapi_app()
        setup_fastapi_ioc(container=container, app=fastapi_app)

        uvicorn_config = uvicorn.Config(
            fastapi_app,
            host="0.0.0.0",
            port=port,
            log_config=None,
        )
        server = uvicorn.Server(uvicorn_config)
        await server.serve()

    finally:
        await container.close()


def start_app(port: int = 8000) -> None:
    asyncio.run(_start_app(port=port))


if __name__ == "__main__":
    start_app()
