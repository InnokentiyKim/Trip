import time

import structlog
from asgi_correlation_id import correlation_id
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.config import create_configs

config = create_configs()
access_logger = structlog.stdlib.get_logger(config.logger.api_logger_name)


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Middleware to log access details for each HTTP request.

        Args:
            request: The incoming Starlette request object.
            call_next: The next middleware or endpoint in the chain.

        Returns:
            Response: The outgoing Starlette response object.
        """
        if request.scope["type"] != "http":
            return await call_next(request)

        start_time = time.perf_counter()

        response = await call_next(request)

        # Calculate processing time
        process_time_ms = (time.perf_counter() - start_time) * 1000

        if request.url.path in ("/health", "/health/"):
            return response

        # Gather request and response details
        status_code = response.status_code
        client_host, client_port = request.client or (None, None)
        http_method = request.method
        http_version = request.scope["http_version"]
        url_path_with_query = request.url.path + ("?" + request.url.query if request.url.query else "")

        log_context = {
            "http": {
                "url": url_path_with_query,
                "status_code": status_code,
                "method": http_method,
                "version": http_version,
                "request_id": correlation_id.get(),
            },
            "network": {"client": {"ip": client_host, "port": client_port}},
            "duration": round(process_time_ms, 3),
        }

        log_message = (
            f"{client_host or '?.?.?.?'}:{client_port or '?'} - "
            f"'{http_method} {url_path_with_query} HTTP/{http_version}' {status_code}"
            f" in {round(process_time_ms, 3)}ms"
        )
        access_logger.info(log_message, **log_context)

        return response
