"""
Unit tests for Health Check API

Tests for liveness and readiness probes in app/api/health.py
"""
import pytest
from unittest.mock import patch, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.unit
class TestLivenessProbe:
    """Test liveness probe endpoint /health"""

    def test_liveness_returns_ok(self):
        """Liveness probe always returns ok status"""
        from app.api.health import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_liveness_is_fast(self):
        """Liveness should respond quickly (no dependency checks)"""
        import time
        from app.api.health import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)

        start = time.perf_counter()
        response = client.get("/health")
        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 0.5  # Should be very fast


@pytest.mark.unit
class TestReadinessProbe:
    """Test readiness probe endpoint /health/ready"""

    def _create_test_app(self, mock_db=None):
        """Create a test app with health router and mocked dependencies"""
        from app.api.health import router

        app = FastAPI()

        # Override get_db dependency
        if mock_db is not None:
            def get_mock_db():
                return mock_db

            app.dependency_overrides[self._get_db_dependency()] = get_mock_db

        app.include_router(router)
        return app

    def _get_db_dependency(self):
        """Get the actual get_db dependency for overriding"""
        from app.db.session import get_db
        return get_db

    def test_readiness_returns_checks(self):
        """Readiness returns checks for all dependencies"""
        mock_db = Mock(spec=Session)
        mock_db.execute = Mock()

        with patch("app.api.health.check_database") as mock_check_db, \
             patch("app.api.health.check_qdrant") as mock_check_qdrant, \
             patch("app.api.health.check_dynamodb") as mock_check_dynamo:

            mock_check_db.return_value = {"status": "ok", "latency_ms": 5}
            mock_check_qdrant.return_value = {"status": "ok", "latency_ms": 10}
            mock_check_dynamo.return_value = {"status": "ok", "latency_ms": 15}

            app = self._create_test_app(mock_db)
            client = TestClient(app)

            response = client.get("/health/ready")
            assert response.status_code == 200
            data = response.json()

            assert "status" in data
            assert "checks" in data
            assert "timestamp" in data

            # Should have checks for database, qdrant, dynamodb
            assert "database" in data["checks"]
            assert "qdrant" in data["checks"]
            assert "dynamodb" in data["checks"]

    def test_readiness_ok_when_all_healthy(self):
        """Readiness returns ok when all dependencies healthy"""
        mock_db = Mock(spec=Session)
        mock_db.execute = Mock()

        with patch("app.api.health.check_database") as mock_check_db, \
             patch("app.api.health.check_qdrant") as mock_check_qdrant, \
             patch("app.api.health.check_dynamodb") as mock_check_dynamo:

            mock_check_db.return_value = {"status": "ok", "latency_ms": 5}
            mock_check_qdrant.return_value = {"status": "ok", "latency_ms": 10}
            mock_check_dynamo.return_value = {"status": "ok", "latency_ms": 15}

            app = self._create_test_app(mock_db)
            client = TestClient(app)

            response = client.get("/health/ready")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"

    def test_readiness_degraded_on_db_failure(self):
        """Readiness returns degraded/error when database fails"""
        mock_db = Mock(spec=Session)
        mock_db.execute = Mock(side_effect=Exception("Connection refused"))

        with patch("app.api.health.check_database") as mock_check_db, \
             patch("app.api.health.check_qdrant") as mock_check_qdrant, \
             patch("app.api.health.check_dynamodb") as mock_check_dynamo:

            mock_check_db.return_value = {"status": "error", "error": "connection failed"}
            mock_check_qdrant.return_value = {"status": "ok", "latency_ms": 10}
            mock_check_dynamo.return_value = {"status": "ok", "latency_ms": 15}

            app = self._create_test_app(mock_db)
            client = TestClient(app)

            response = client.get("/health/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ("degraded", "error")
            assert data["checks"]["database"]["status"] == "error"

    def test_readiness_ok_when_skipped(self):
        """Readiness returns ok when dependencies are skipped (not configured)"""
        mock_db = Mock(spec=Session)
        mock_db.execute = Mock()

        with patch("app.api.health.check_database") as mock_check_db, \
             patch("app.api.health.check_qdrant") as mock_check_qdrant, \
             patch("app.api.health.check_dynamodb") as mock_check_dynamo:

            mock_check_db.return_value = {"status": "ok", "latency_ms": 5}
            mock_check_qdrant.return_value = {"status": "skipped", "reason": "not configured"}
            mock_check_dynamo.return_value = {"status": "skipped", "reason": "not configured"}

            app = self._create_test_app(mock_db)
            client = TestClient(app)

            response = client.get("/health/ready")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"


@pytest.mark.unit
class TestDetailedHealth:
    """Test detailed health endpoint /health/detailed"""

    def test_detailed_returns_system_info(self):
        """Detailed health returns system information"""
        from app.api.health import router
        from app.db.session import get_db

        mock_db = Mock(spec=Session)
        mock_db.execute = Mock()

        app = FastAPI()

        def get_mock_db():
            return mock_db

        app.dependency_overrides[get_db] = get_mock_db
        app.include_router(router)

        with patch("app.api.health.check_database") as mock_check_db, \
             patch("app.api.health.check_qdrant") as mock_check_qdrant, \
             patch("app.api.health.check_dynamodb") as mock_check_dynamo:

            mock_check_db.return_value = {"status": "ok", "latency_ms": 5}
            mock_check_qdrant.return_value = {"status": "ok", "latency_ms": 10}
            mock_check_dynamo.return_value = {"status": "ok", "latency_ms": 15}

            client = TestClient(app)
            response = client.get("/health/detailed")

            assert response.status_code == 200
            data = response.json()

            assert "status" in data
            assert "checks" in data
            assert "system" in data
            assert "python_version" in data["system"]
            assert "platform" in data["system"]


@pytest.mark.unit
class TestHealthCheckFunctions:
    """Test individual health check functions"""

    @pytest.mark.asyncio
    async def test_check_database_success(self):
        """check_database returns ok on successful connection"""
        from app.api.health import check_database

        mock_db = Mock(spec=Session)
        mock_db.execute = Mock()

        result = await check_database(mock_db)

        assert result["status"] == "ok"
        assert "latency_ms" in result
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_database_failure(self):
        """check_database returns error on connection failure"""
        from app.api.health import check_database

        mock_db = Mock(spec=Session)
        mock_db.execute = Mock(side_effect=Exception("Connection refused"))

        result = await check_database(mock_db)

        assert result["status"] == "error"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_check_qdrant_skipped_when_not_configured(self):
        """check_qdrant returns skipped when not configured"""
        from app.api.health import check_qdrant

        with patch("app.api.health.settings") as mock_settings:
            mock_settings.QDRANT_HOST = ""
            mock_settings.QDRANT_URL = ""

            result = await check_qdrant()

            assert result["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_check_dynamodb_skipped_when_not_configured(self):
        """check_dynamodb returns skipped when not configured"""
        from app.api.health import check_dynamodb

        with patch("app.api.health.settings") as mock_settings:
            mock_settings.DDB_EVIDENCE_TABLE = ""

            result = await check_dynamodb()

            assert result["status"] == "skipped"
