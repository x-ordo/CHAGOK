"""
Unit tests for Correlation ID Middleware

Tests for app/middleware/correlation.py
"""
import pytest
import uuid
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middleware.correlation import (
    CorrelationIdMiddleware,
    CORRELATION_ID_HEADER,
    get_correlation_id_from_request
)


@pytest.mark.unit
class TestCorrelationIdMiddleware:
    """Test CorrelationIdMiddleware functionality"""

    def test_generates_correlation_id_if_missing(self):
        """Generate UUID if X-Request-ID not provided"""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert CORRELATION_ID_HEADER in response.headers

        # Verify UUID format (should be 36 chars: 8-4-4-4-12)
        correlation_id = response.headers[CORRELATION_ID_HEADER]
        assert len(correlation_id) == 36
        assert correlation_id.count("-") == 4

        # Verify it's a valid UUID
        try:
            uuid.UUID(correlation_id)
        except ValueError:
            pytest.fail(f"Invalid UUID format: {correlation_id}")

    def test_preserves_existing_correlation_id(self):
        """Preserve X-Request-ID if already provided"""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        existing_id = "my-custom-correlation-id-12345"
        response = client.get(
            "/test",
            headers={CORRELATION_ID_HEADER: existing_id}
        )

        assert response.status_code == 200
        assert response.headers[CORRELATION_ID_HEADER] == existing_id

    def test_correlation_id_available_in_request_state(self):
        """Correlation ID should be accessible in request.state"""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        captured_correlation_id = None

        @app.get("/test")
        async def test_endpoint(request: Request):
            nonlocal captured_correlation_id
            captured_correlation_id = request.state.correlation_id
            return {"correlation_id": captured_correlation_id}

        client = TestClient(app)
        custom_id = "test-request-id-xyz"
        response = client.get(
            "/test",
            headers={CORRELATION_ID_HEADER: custom_id}
        )

        assert response.status_code == 200
        assert captured_correlation_id == custom_id
        assert response.json()["correlation_id"] == custom_id

    def test_different_requests_get_different_ids(self):
        """Each request without header gets unique correlation ID"""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)

        response1 = client.get("/test")
        response2 = client.get("/test")

        id1 = response1.headers[CORRELATION_ID_HEADER]
        id2 = response2.headers[CORRELATION_ID_HEADER]

        assert id1 != id2

    def test_works_with_http_exception_responses(self):
        """Correlation ID should be added on HTTPException responses"""
        from fastapi import HTTPException

        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/error")
        async def error_endpoint():
            raise HTTPException(status_code=404, detail="Not found")

        client = TestClient(app)
        response = client.get("/error")

        # HTTPException responses should still have correlation ID
        assert response.status_code == 404
        assert CORRELATION_ID_HEADER in response.headers

    def test_works_with_post_requests(self):
        """Correlation ID works with POST requests"""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.post("/test")
        async def test_endpoint():
            return {"message": "created"}

        client = TestClient(app)
        response = client.post("/test")

        assert response.status_code == 200
        assert CORRELATION_ID_HEADER in response.headers


@pytest.mark.unit
class TestGetCorrelationIdFromRequest:
    """Test utility function get_correlation_id_from_request"""

    def test_returns_correlation_id_from_state(self):
        """Returns correlation ID from request.state"""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        captured_id = None

        @app.get("/test")
        async def test_endpoint(request: Request):
            nonlocal captured_id
            captured_id = get_correlation_id_from_request(request)
            return {"id": captured_id}

        client = TestClient(app)
        custom_id = "custom-test-id"
        client.get(
            "/test",
            headers={CORRELATION_ID_HEADER: custom_id}
        )

        assert captured_id == custom_id

    def test_returns_unknown_when_not_set(self):
        """Returns 'unknown' when correlation ID not in state"""
        from starlette.requests import Request

        # Create a mock request without correlation ID in state
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(request: Request):
            # Don't use middleware, so no correlation ID
            result = get_correlation_id_from_request(request)
            return {"id": result}

        client = TestClient(app)
        response = client.get("/test")

        assert response.json()["id"] == "unknown"


@pytest.mark.unit
class TestCorrelationIdHeader:
    """Test header name constant"""

    def test_header_name_is_x_request_id(self):
        """Header name should be X-Request-ID"""
        assert CORRELATION_ID_HEADER == "X-Request-ID"


@pytest.mark.unit
class TestMiddlewareIntegration:
    """Test middleware integration scenarios"""

    def test_works_with_other_middleware(self):
        """Correlation ID middleware works with other middleware"""
        from starlette.middleware.base import BaseHTTPMiddleware

        class DummyMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                response = await call_next(request)
                response.headers["X-Dummy"] = "test"
                return response

        app = FastAPI()
        app.add_middleware(DummyMiddleware)
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test")

        assert CORRELATION_ID_HEADER in response.headers
        assert "X-Dummy" in response.headers

    def test_correlation_id_flows_through_request(self):
        """Correlation ID flows from request to response"""
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            # Access the correlation ID from request state
            req_id = request.state.correlation_id
            return {"request_correlation_id": req_id}

        client = TestClient(app)
        custom_id = "flow-test-id"
        response = client.get(
            "/test",
            headers={CORRELATION_ID_HEADER: custom_id}
        )

        # Should match in both places
        assert response.headers[CORRELATION_ID_HEADER] == custom_id
        assert response.json()["request_correlation_id"] == custom_id
