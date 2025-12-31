"""
CHAGOK - Configuration
Environment variables and application settings using Pydantic Settings

Secrets Management:
- Local/Test: Uses environment variables directly
- Dev/Prod: Fetches secrets from AWS Secrets Manager (if available)
"""

import json
import logging
import os
import warnings
from functools import lru_cache
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator

logger = logging.getLogger(__name__)


# ============================================
# AWS Secrets Manager Integration
# ============================================
@lru_cache(maxsize=1)
def get_secrets_from_aws(secret_name: str = "chagok/secrets") -> Dict[str, str]:
    """
    Fetch secrets from AWS Secrets Manager.
    Returns empty dict if not available or in local environment.

    Secret Structure in AWS Secrets Manager:
    {
        "JWT_SECRET": "...",
        "OPENAI_API_KEY": "...",
        "GEMINI_API_KEY": "...",
        "DATABASE_URL": "...",
        "QDRANT_API_KEY": "...",
        "INTERNAL_API_KEY": "..."
    }
    """
    app_env = os.environ.get("APP_ENV", "local")

    # Skip AWS Secrets Manager for local development
    if app_env in ("local", "test"):
        logger.debug("Skipping AWS Secrets Manager in local/test environment")
        return {}

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        region = os.environ.get("AWS_REGION", "ap-northeast-2")
        client = boto3.client("secretsmanager", region_name=region)

        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString", "{}")
        secrets = json.loads(secret_string)

        logger.info(f"Loaded {len(secrets)} secrets from AWS Secrets Manager")
        return secrets

    except ImportError:
        logger.warning("boto3 not installed, skipping AWS Secrets Manager")
        return {}
    except NoCredentialsError:
        logger.warning("No AWS credentials found, using environment variables")
        return {}
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "ResourceNotFoundException":
            logger.warning(f"Secret '{secret_name}' not found in AWS Secrets Manager")
        else:
            logger.warning(f"Failed to fetch secrets from AWS: {error_code}")
        return {}
    except Exception as e:
        logger.warning(f"Unexpected error fetching secrets: {e}")
        return {}


def get_secret_value(key: str, default: str = "") -> str:
    """
    Get a secret value with priority:
    1. Environment variable (highest priority for overrides)
    2. AWS Secrets Manager
    3. Default value
    """
    # Environment variable takes precedence (allows overrides)
    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value

    # Try AWS Secrets Manager
    secrets = get_secrets_from_aws()
    if key in secrets:
        return secrets[key]

    return default


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables
    """

    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = Field(default="chagok", env="APP_NAME")
    APP_ENV: str = Field(default="local", env="APP_ENV")  # local | dev | prod
    APP_DEBUG: bool = Field(default=True, env="APP_DEBUG")

    # ============================================
    # Backend Server Settings
    # ============================================
    BACKEND_HOST: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    BACKEND_PORT: int = Field(default=8000, env="BACKEND_PORT")
    BACKEND_LOG_LEVEL: str = Field(default="INFO", env="BACKEND_LOG_LEVEL")

    # ============================================
    # CORS Settings
    # ============================================
    BACKEND_CORS_ORIGINS: str = Field(default="", env="BACKEND_CORS_ORIGINS")
    CORS_ALLOW_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004,http://localhost:3005,http://localhost:5173",
        env="CORS_ALLOW_ORIGINS"
    )
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins as a list"""
        raw = self.BACKEND_CORS_ORIGINS or self.CORS_ALLOW_ORIGINS or ""
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    # ============================================
    # JWT Settings
    # ============================================
    JWT_SECRET: str = Field(default="local-dev-secret-change-in-prod-min-32-chars", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    @model_validator(mode='after')
    def validate_jwt_secret_for_production(self):
        """
        Validate JWT_SECRET in production environment.
        - Must be at least 32 characters
        - Must not be the default value
        """
        default_secret = "local-dev-secret-change-in-prod-min-32-chars"

        if self.APP_ENV in ("prod", "production"):
            # In production, enforce strict validation
            if self.JWT_SECRET == default_secret:
                raise ValueError(
                    "JWT_SECRET must be changed from default value in production. "
                    "Generate a strong secret: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            if len(self.JWT_SECRET) < 32:
                raise ValueError(
                    f"JWT_SECRET must be at least 32 characters in production (current: {len(self.JWT_SECRET)})"
                )
        elif self.APP_ENV == "dev":
            # In dev environment, warn but don't fail
            if self.JWT_SECRET == default_secret:
                warnings.warn(
                    "Using default JWT_SECRET in dev environment. "
                    "Set a strong secret before deploying to production.",
                    UserWarning
                )

        return self

    # ============================================
    # Cookie Settings
    # ============================================
    # Note: For cross-origin (CloudFront → API), production MUST use:
    #   COOKIE_SECURE=true, COOKIE_SAMESITE=none
    # These are auto-configured based on APP_ENV if not explicitly set.
    COOKIE_SECURE: bool = Field(default=False, env="COOKIE_SECURE")  # True in production (HTTPS)
    COOKIE_SAMESITE: str = Field(default="lax", env="COOKIE_SAMESITE")  # lax | strict | none
    COOKIE_DOMAIN: str = Field(default="", env="COOKIE_DOMAIN")  # Empty = current domain

    @model_validator(mode='after')
    def validate_cookie_settings_for_production(self):
        """
        Auto-configure cookie settings for cross-origin in production/dev environments.
        Cross-origin (CloudFront frontend → API backend) requires:
        - SameSite=None (allows cross-site cookie transmission)
        - Secure=True (required when SameSite=None, HTTPS only)
        """
        import os

        # Check if explicitly set via environment variable
        explicit_samesite = os.environ.get("COOKIE_SAMESITE")
        explicit_secure = os.environ.get("COOKIE_SECURE")

        if self.APP_ENV in ("prod", "production", "dev"):
            # Auto-configure for cross-origin if not explicitly set
            if explicit_samesite is None:
                self.COOKIE_SAMESITE = "none"
            if explicit_secure is None:
                self.COOKIE_SECURE = True

            # Validate SameSite=None requires Secure=True
            if self.COOKIE_SAMESITE.lower() == "none" and not self.COOKIE_SECURE:
                raise ValueError(
                    "COOKIE_SECURE must be True when COOKIE_SAMESITE is 'none'. "
                    "Cross-origin cookies require both settings for security."
                )

        return self

    # ============================================
    # Public API Base URL (used by frontend/backoffice)
    # ============================================
    API_BASE_URL: str = Field(default="", env="API_BASE_URL")

    # ============================================
    # Database Settings (PostgreSQL)
    # ============================================
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(default="leh_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="leh_db", env="POSTGRES_DB")

    DATABASE_URL: str = Field(default="", env="DATABASE_URL")

    @property
    def database_url_computed(self) -> str:
        """
        Construct database URL from individual components if DATABASE_URL is not set
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ============================================
    # AWS Settings
    # ============================================
    AWS_REGION: str = Field(default="ap-northeast-2", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")

    # ============================================
    # AWS SES Settings
    # ============================================
    SES_SENDER_EMAIL: str = Field(default="", env="SES_SENDER_EMAIL")

    # ============================================
    # S3 Settings
    # ============================================
    S3_EVIDENCE_BUCKET: str = Field(default="leh-evidence-prod", env="S3_EVIDENCE_BUCKET")
    S3_EVIDENCE_PREFIX: str = Field(default="cases/", env="S3_EVIDENCE_PREFIX")
    S3_PRESIGNED_URL_EXPIRE_SECONDS: int = Field(default=300, env="S3_PRESIGNED_URL_EXPIRE_SECONDS")  # 5 minutes max

    # ============================================
    # Lambda Settings (AI Worker)
    # ============================================
    LAMBDA_AI_WORKER_FUNCTION: str = Field(default="leh-ai-worker", env="LAMBDA_AI_WORKER_FUNCTION")
    LAMBDA_AI_WORKER_ENABLED: bool = Field(default=True, env="LAMBDA_AI_WORKER_ENABLED")

    # ============================================
    # DynamoDB Settings
    # ============================================
    DDB_EVIDENCE_TABLE: str = Field(default="leh_evidence", env="DDB_EVIDENCE_TABLE")
    DDB_CASE_SUMMARY_TABLE: str = Field(default="leh_case_summary", env="DDB_CASE_SUMMARY_TABLE")

    # ============================================
    # Qdrant Settings (Vector Database for RAG)
    # ============================================
    QDRANT_URL: str = Field(default="", env="QDRANT_URL")
    QDRANT_HOST: str = Field(default="", env="QDRANT_HOST")  # Empty = in-memory mode
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_API_KEY: str = Field(default="", env="QDRANT_API_KEY")
    QDRANT_USE_HTTPS: bool = Field(default=False, env="QDRANT_USE_HTTPS")
    QDRANT_COLLECTION_PREFIX: str = Field(default="case_rag_", env="QDRANT_COLLECTION_PREFIX")
    QDRANT_COLLECTION: str = Field(default="leh_evidence", env="QDRANT_COLLECTION")
    QDRANT_DEFAULT_TOP_K: int = Field(default=5, env="QDRANT_DEFAULT_TOP_K")
    QDRANT_VECTOR_SIZE: int = Field(default=1536, env="QDRANT_VECTOR_SIZE")

    # ============================================
    # OpenAI / LLM Settings
    # ============================================
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_API_BASE: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE")
    OPENAI_MODEL_CHAT: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL_CHAT")
    OPENAI_MODEL_EMBEDDING: str = Field(default="text-embedding-3-small", env="OPENAI_MODEL_EMBEDDING")

    # Gemini API Settings (for draft generation - faster than OpenAI)
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL_CHAT: str = Field(default="gemini-3-flash-preview", env="GEMINI_MODEL_CHAT")
    USE_GEMINI_FOR_DRAFT: bool = Field(default=True, env="USE_GEMINI_FOR_DRAFT")

    LLM_REQUEST_TIMEOUT_SECONDS: int = Field(default=60, env="LLM_REQUEST_TIMEOUT_SECONDS")  # Async draft uses Lambda 90s timeout

    # ============================================
    # Feature Flags
    # ============================================
    FEATURE_DRAFT_PREVIEW_ONLY: bool = Field(default=True, env="FEATURE_DRAFT_PREVIEW_ONLY")
    FEATURE_ENABLE_RAG_SEARCH: bool = Field(default=True, env="FEATURE_ENABLE_RAG_SEARCH")
    FEATURE_ENABLE_TIMELINE_VIEW: bool = Field(default=True, env="FEATURE_ENABLE_TIMELINE_VIEW")

    # ============================================
    # Internal API Security
    # ============================================
    INTERNAL_API_KEY: str = Field(default="", env="INTERNAL_API_KEY")  # For AI Worker callbacks

    # ============================================
    # Logging / Monitoring
    # ============================================
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")  # json | text
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=True,
        extra="ignore"
    )

    @model_validator(mode='after')
    def load_secrets_from_aws(self):
        """
        Load sensitive secrets from AWS Secrets Manager in dev/prod environments.
        Environment variables take precedence over AWS Secrets Manager.
        """
        if self.APP_ENV in ("local", "test"):
            return self

        # List of fields that should be loaded from Secrets Manager
        secret_fields = [
            "JWT_SECRET",
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "DATABASE_URL",
            "QDRANT_API_KEY",
            "INTERNAL_API_KEY",
        ]

        secrets = get_secrets_from_aws()
        if not secrets:
            return self

        for field_name in secret_fields:
            # Only update if not explicitly set in environment
            if not os.environ.get(field_name) and field_name in secrets:
                current_value = getattr(self, field_name, None)
                # Only update if current value is empty or default
                if not current_value or current_value in (
                    "",
                    "local-dev-secret-change-in-prod-min-32-chars"
                ):
                    setattr(self, field_name, secrets[field_name])
                    logger.debug(f"Loaded {field_name} from AWS Secrets Manager")

        return self


# ============================================
# Global settings instance
# ============================================
settings = Settings()
