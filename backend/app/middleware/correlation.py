"""
Correlation ID Middleware

Adds X-Request-ID header to all requests for distributed tracing.
This enables request tracking across multiple services and log correlation.

Usage:
    app.add_middleware(CorrelationIdMiddleware)

The correlation ID is:
    - Taken from incoming X-Request-ID header if present
    - Generated as UUID if not present
    - Added to response headers for client tracking
    - Stored in request.state for use in logging
"""
import uuid
import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Header name constant - can be overridden if needed
CORRELATION_ID_HEADER = "X-Request-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation ID to all requests.

    Features:
        - Preserves existing X-Request-ID header if provided by client
        - Generates new UUID v4 if no header present
        - Adds correlation ID to response headers for tracing
        - Stores correlation ID in request.state for logging

    Example:
        # In your FastAPI app
        app.add_middleware(CorrelationIdMiddleware)

        # Access in route handlers
        @app.get("/example")
        async def example(request: Request):
            correlation_id = request.state.correlation_id
            logger.info(f"Processing request {correlation_id}")
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process the request and add correlation ID.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response with X-Request-ID header
        """
        # Get existing correlation ID or generate new one
        correlation_id = request.headers.get(
            CORRELATION_ID_HEADER,
            str(uuid.uuid4())
        )

        # Store in request state for downstream access
        request.state.correlation_id = correlation_id

        # Log incoming request with correlation ID
        logger.debug(
            f"Request {request.method} {request.url.path} "
            f"[{correlation_id}]"
        )

        # Process the request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response


def get_correlation_id_from_request(request: Request) -> str:
    """
    Utility function to get correlation ID from request state.

    Args:
        request: FastAPI Request object

    Returns:
        Correlation ID string, or "unknown" if not set

    Example:
        @app.get("/example")
        async def example(request: Request):
            correlation_id = get_correlation_id_from_request(request)
            logger.info(f"[{correlation_id}] Processing...")
    """
    return getattr(request.state, "correlation_id", "unknown")


def get_correlation_id_middleware() -> type:
    """
    Factory function to get CorrelationIdMiddleware class.

    Useful for dependency injection or configuration.

    Returns:
        CorrelationIdMiddleware class
    """
    return CorrelationIdMiddleware
