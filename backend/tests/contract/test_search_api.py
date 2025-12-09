"""
Contract tests for Search API
007-lawyer-portal-v1: US6 (Global Search)
009-mvp-gap-closure: US2 (RAG Semantic Search)
"""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestSearchAPI:
    """Contract tests for GET /search endpoint"""

    def test_search_requires_auth(self, client: TestClient):
        """Test that search endpoint requires authentication"""
        response = client.get("/search?q=test")
        assert response.status_code == 401

    def test_search_requires_min_query_length(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that search requires minimum 2 character query"""
        response = client.get("/search?q=a", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_search_returns_results_structure(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test that search returns proper result structure"""
        response = client.get("/search?q=test", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "query" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)

    def test_search_cases_by_title(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test searching cases by title"""
        # test_case fixture creates a case with title containing "테스트"
        response = client.get("/search?q=테스트&categories=cases", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] >= 0  # May find test case

        # Verify result structure if results found
        for result in data["results"]:
            assert result["category"] == "cases"
            assert "id" in result
            assert "title" in result
            assert "subtitle" in result
            assert "icon" in result
            assert "url" in result

    def test_search_with_category_filter(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test searching with specific category filter"""
        response = client.get(
            "/search?q=test&categories=cases,evidence",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # All results should be in filtered categories
        for result in data["results"]:
            assert result["category"] in ["cases", "evidence"]

    def test_search_with_limit(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test search respects limit parameter"""
        response = client.get("/search?q=test&limit=5", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Results per category should not exceed limit
        category_counts = {}
        for result in data["results"]:
            cat = result["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for count in category_counts.values():
            assert count <= 5

    def test_search_empty_query_returns_empty(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that short query returns empty results"""
        # Query with exactly 2 chars should work
        response = client.get("/search?q=ab", headers=auth_headers)
        assert response.status_code == 200

    def test_search_result_contains_metadata(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test that search results contain metadata"""
        response = client.get("/search?q=테스트", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for result in data["results"]:
            assert "metadata" in result
            assert isinstance(result["metadata"], dict)


class TestQuickAccessAPI:
    """Contract tests for GET /search/quick-access endpoint"""

    def test_quick_access_requires_auth(self, client: TestClient):
        """Test that quick-access endpoint requires authentication"""
        response = client.get("/search/quick-access")
        assert response.status_code == 401

    def test_quick_access_returns_structure(
        self, client: TestClient, auth_headers: dict
    ):
        """Test quick-access returns proper structure"""
        response = client.get("/search/quick-access", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "todays_events" in data
        assert "todays_events_count" in data
        assert isinstance(data["todays_events"], list)
        assert isinstance(data["todays_events_count"], int)


class TestRecentSearchesAPI:
    """Contract tests for GET /search/recent endpoint"""

    def test_recent_searches_requires_auth(self, client: TestClient):
        """Test that recent-searches endpoint requires authentication"""
        response = client.get("/search/recent")
        assert response.status_code == 401

    def test_recent_searches_returns_structure(
        self, client: TestClient, auth_headers: dict
    ):
        """Test recent-searches returns proper structure"""
        response = client.get("/search/recent", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "recent_searches" in data
        assert isinstance(data["recent_searches"], list)

    def test_recent_searches_respects_limit(
        self, client: TestClient, auth_headers: dict
    ):
        """Test recent-searches respects limit parameter"""
        response = client.get("/search/recent?limit=3", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["recent_searches"]) <= 3


class TestSemanticSearchAPI:
    """Contract tests for GET /search/semantic endpoint (RAG Qdrant search)"""

    def test_semantic_search_requires_auth(self, client: TestClient):
        """Test that semantic search endpoint requires authentication"""
        response = client.get("/search/semantic?q=test&case_id=case_123")
        assert response.status_code == 401

    def test_semantic_search_requires_case_id(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that semantic search requires case_id parameter"""
        response = client.get("/search/semantic?q=test", headers=auth_headers)
        assert response.status_code == 422  # Validation error - missing case_id

    def test_semantic_search_requires_min_query_length(
        self, client: TestClient, auth_headers: dict, test_case
    ):
        """Test that semantic search requires minimum 2 character query"""
        response = client.get(
            f"/search/semantic?q=a&case_id={test_case.id}",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_semantic_search_returns_403_for_non_member(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that semantic search returns 403 for non-case-member"""
        # Using a non-existent case_id
        response = client.get(
            "/search/semantic?q=test&case_id=case_nonexistent",
            headers=auth_headers
        )
        assert response.status_code == 403

    @patch('app.api.search.search_evidence_by_semantic')
    def test_semantic_search_returns_results_structure(
        self,
        mock_qdrant_search: MagicMock,
        client: TestClient,
        auth_headers: dict,
        test_case
    ):
        """Test that semantic search returns proper result structure"""
        # Mock Qdrant response
        mock_qdrant_search.return_value = [
            {
                "evidence_id": "ev_001",
                "content": "테스트 증거 내용",
                "labels": ["폭언"],
                "_score": 0.95
            }
        ]

        response = client.get(
            f"/search/semantic?q=test&case_id={test_case.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "query" in data
        assert "case_id" in data
        assert "results" in data
        assert "total" in data
        assert data["case_id"] == test_case.id
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)

    @patch('app.api.search.search_evidence_by_semantic')
    def test_semantic_search_with_labels_filter(
        self,
        mock_qdrant_search: MagicMock,
        client: TestClient,
        auth_headers: dict,
        test_case
    ):
        """Test semantic search with labels filter"""
        mock_qdrant_search.return_value = []

        response = client.get(
            f"/search/semantic?q=test&case_id={test_case.id}&labels=폭언,불륜",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify filter was passed to Qdrant
        mock_qdrant_search.assert_called_once()
        call_kwargs = mock_qdrant_search.call_args[1]
        assert call_kwargs["filters"] == {"labels": ["폭언", "불륜"]}

    @patch('app.api.search.search_evidence_by_semantic')
    def test_semantic_search_respects_top_k(
        self,
        mock_qdrant_search: MagicMock,
        client: TestClient,
        auth_headers: dict,
        test_case
    ):
        """Test semantic search respects top_k parameter"""
        mock_qdrant_search.return_value = []

        response = client.get(
            f"/search/semantic?q=test&case_id={test_case.id}&top_k=10",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify top_k was passed to Qdrant
        mock_qdrant_search.assert_called_once()
        call_kwargs = mock_qdrant_search.call_args[1]
        assert call_kwargs["top_k"] == 10

    @patch('app.api.search.search_evidence_by_semantic')
    def test_semantic_search_enforces_case_isolation(
        self,
        mock_qdrant_search: MagicMock,
        client: TestClient,
        auth_headers: dict,
        test_case
    ):
        """Test that semantic search only searches within specified case_id"""
        mock_qdrant_search.return_value = []

        response = client.get(
            f"/search/semantic?q=test&case_id={test_case.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify case_id was passed to Qdrant (case isolation)
        mock_qdrant_search.assert_called_once()
        call_kwargs = mock_qdrant_search.call_args[1]
        assert call_kwargs["case_id"] == test_case.id
