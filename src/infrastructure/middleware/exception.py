import structlog
from src.config import create_configs
from fastapi import status
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

config = create_configs()
exception_logger = structlog.stdlib.get_logger(config.logger.api_logger_name)


class UnhandledExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Processes the request, handles any unhandled exceptions, and returns the response.

        Args:
            request: The incoming Starlette request object.
            call_next: The next middleware or endpoint in the chain.

        Returns:
            Response: The outgoing Starlette response object.
        """
        try:
            return await call_next(request)
        except Exception as exc:
            exception_logger.error(
                "An unhandled exception occurred",
                exception_class=exc.__class__.__name__,
                path=request.url.path,
                exc_info=True,
            )

            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal Server Error"},
            )
