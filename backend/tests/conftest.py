"""
Pytest configuration and shared fixtures for LEH Backend tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import os


# ============================================
# Auto-use AWS Mocking Fixtures
# ============================================

@pytest.fixture(scope="session", autouse=True)
def mock_aws_services():
    """
    Mock all AWS services (S3, DynamoDB) at session level
    to prevent tests from requiring real AWS credentials
    """
    mock_boto3_client = MagicMock()
    mock_boto3_resource = MagicMock()

    # Mock DynamoDB Table
    mock_table = MagicMock()
    mock_table.query.return_value = {"Items": []}
    mock_table.scan.return_value = {"Items": []}
    mock_table.get_item.return_value = {"Item": None}
    mock_table.put_item.return_value = {}
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Mock S3 client
    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/presigned-url"
    mock_s3.generate_presigned_post.return_value = {
        "url": "https://test-bucket.s3.amazonaws.com",
        "fields": {"key": "test-key"}
    }
    mock_boto3_client.return_value = mock_s3

    with patch('boto3.client', mock_boto3_client), \
         patch('boto3.resource', mock_boto3_resource):
        yield {
            "s3": mock_s3,
            "dynamodb_table": mock_table,
        }


@pytest.fixture(scope="session")
def test_env():
    """
    Set up test environment variables and initialize database
    """
    import os as os_module

    # Clean up any existing test database
    if os_module.path.exists("./test.db"):
        os_module.remove("./test.db")

    test_env_vars = {
        "APP_ENV": "local",
        "APP_DEBUG": "true",
        "JWT_SECRET": "test-secret-key-do-not-use-in-production",
        "DATABASE_URL": "sqlite:///./test.db",
        "S3_EVIDENCE_BUCKET": "test-bucket",
        "DDB_EVIDENCE_TABLE": "test-evidence-table",
        "OPENSEARCH_HOST": "https://test-opensearch.local",
        "OPENAI_API_KEY": "test-openai-key",
    }

    # Store original env vars
    original_env = {}
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    # Patch global settings
    from app.core.config import settings
    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = test_env_vars["DATABASE_URL"]

    # Initialize database and create tables for all tests
    from app.db.session import init_db, engine
    from app.db.models import Base
    init_db()

    yield test_env_vars

    # Drop tables and cleanup
    if engine is not None:
        Base.metadata.drop_all(bind=engine)

    # Restore global settings
    settings.DATABASE_URL = original_db_url

    # Restore original env vars
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value

    # Clean up test database file
    if os_module.path.exists("./test.db"):
        os_module.remove("./test.db")


@pytest.fixture(scope="function")
def client(test_env):
    """
    FastAPI TestClient fixture

    Creates a fresh TestClient for each test function.
    Automatically uses test environment variables.
    """
    # Import here to ensure test_env is loaded first
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def mock_settings(test_env):
    """
    Mock settings object for unit tests

    Returns a settings object with test values.
    """
    from app.core.config import Settings

    settings = Settings(**test_env)
    return settings


@pytest.fixture(scope="function")
def mock_db_session():
    """
    Mock database session

    Use this for testing database operations without real DB.
    """
    session = Mock()
    yield session
    session.close()


@pytest.fixture(scope="function")
def mock_s3_client():
    """
    Mock boto3 S3 client
    """
    with patch('boto3.client') as mock_boto3:
        mock_client = Mock()
        mock_boto3.return_value = mock_client
        yield mock_client


@pytest.fixture(scope="function")
def mock_dynamodb_client():
    """
    Mock boto3 DynamoDB client
    """
    with patch('boto3.resource') as mock_boto3:
        mock_resource = Mock()
        mock_boto3.return_value = mock_resource
        yield mock_resource


@pytest.fixture(scope="function")
def mock_opensearch_client():
    """
    Mock OpenSearch client
    """
    with patch('opensearchpy.OpenSearch') as mock_os:
        mock_client = Mock()
        mock_os.return_value = mock_client
        yield mock_client


@pytest.fixture(scope="function")
def mock_openai_client():
    """
    Mock OpenAI client
    """
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_case_data():
    """
    Sample case data for testing
    """
    return {
        "id": "case_123",
        "title": "김○○ 이혼 사건",
        "description": "테스트 사건",
        "status": "active",
        "created_by": "user_456"
    }


@pytest.fixture
def sample_evidence_data():
    """
    Sample evidence metadata for testing
    """
    return {
        "case_id": "case_123",
        "evidence_id": "ev_001",
        "type": "text",
        "timestamp": "2024-12-25T10:20:00Z",
        "speaker": "원고",
        "labels": ["폭언", "계속적 불화"],
        "ai_summary": "피고가 고성을 지르며 폭언함",
        "content": "테스트 증거 내용",
        "s3_key": "cases/case_123/raw/test.txt",
        "status": "done"
    }


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing
    """
    return {
        "id": "user_456",
        "email": "test@example.com",
        "name": "테스트 사용자",
        "role": "lawyer"
    }


@pytest.fixture
def test_user(test_env):
    """
    Create a real user in the database for authentication tests

    Password: correct_password123
    """
    from app.db.session import get_db
    from app.db.models import User, Case, CaseMember
    from app.core.security import hash_password
    from sqlalchemy.orm import Session

    # Database is already initialized by test_env fixture
    # Create user
    db: Session = next(get_db())
    try:
        user = User(
            email="test@example.com",
            hashed_password=hash_password("correct_password123"),
            name="테스트 사용자",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        yield user

        # Cleanup - delete in correct order to respect foreign keys
        # Delete case_members first
        db.query(CaseMember).filter(CaseMember.user_id == user.id).delete()
        # Delete cases created by user
        db.query(Case).filter(Case.created_by == user.id).delete()
        # Delete user
        db.delete(user)
        db.commit()
    finally:
        db.close()


@pytest.fixture
def auth_headers(test_user):
    """
    Generate authentication headers with JWT token for test_user

    Returns:
        dict: Headers with Authorization Bearer token
    """
    from app.core.security import create_access_token

    # Create JWT token for test user
    token = create_access_token(data={"sub": test_user.id, "role": test_user.role})

    return {
        "Authorization": f"Bearer {token}"
    }
