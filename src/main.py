import asyncio
from typing import Annotated

import typer
import uvicorn
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_ioc

from src.ioc.registry import get_providers
from src.setup.common import create_async_container
from src.setup.fastapi_app import create_fastapi_app

app = typer.Typer()


async def _start_app(port: int) -> None:
    """Start the FastAPI application with IoC container integration."""
    container = create_async_container(get_providers())

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
    """Start the FastAPI application on the specified port."""
    asyncio.run(_start_app(port=port))


@app.command()
def run(
    port: Annotated[int, typer.Option(help="Port for the server to listen on.")] = 8000,
    reload: Annotated[
        bool,
        typer.Option(help="Enable auto-reload on code changes (development only)."),
    ] = False,
) -> None:
    """Run the FastAPI application with optional auto-reload."""
    if reload:
        import subprocess
        import sys

        subprocess.run([
            sys.executable,
            "-m",
            "uvicorn",
            "src.dev_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--reload",
            "--reload-dir",
            "src",
        ])

    asyncio.run(_start_app(port=port))


if __name__ == "__main__":
    start_app()
