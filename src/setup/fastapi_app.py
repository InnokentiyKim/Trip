from fastapi import FastAPI

from src.common.controllers.http.api_v1 import http_router_v1
from src.common.exceptions.common import BaseError
from src.common.exceptions.handlers import general_exception_handler
from src.infrastructure.logger.factory import setup_logging
from src.setup.common import app_config


def create_fastapi_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    This single factory function handles app creation for HTTP services

    Returns:
        The fully configured FastAPI application.
    """
    # Application Initialization
    app = FastAPI(
        version=app_config.general.app_version,
    )

    # Logging setup
    setup_logging(app_config)

    # CORS Configuration (allow frontend to access API)
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=app_config.general.cors.allow_origins,
    #     allow_credentials=app_config.general.cors.allow_credentials,
    #     allow_methods=app_config.general.cors.allow_methods,
    #     allow_headers=app_config.general.cors.allow_headers,
    # )

    # Middleware Configuration

    # Exception handling
    app.add_exception_handler(BaseError, general_exception_handler)

    # API routing
    app.include_router(http_router_v1)

    # Telemetry and metrics

    # Health check endpoint
    # @app.get("/health")
    # async def health_check():
    #     return {"status": "ok"}

    return app
