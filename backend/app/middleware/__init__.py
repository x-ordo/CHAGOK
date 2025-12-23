"""
Legal Evidence Hub (LEH) - Middleware Package
"""

from .error_handler import (
    LEHException,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    ConflictError,
    ValidationError,
    register_exception_handlers
)
from .security import SecurityHeadersMiddleware, HTTPSRedirectMiddleware
from .audit_log import AuditLogMiddleware
from .latency import LatencyLoggingMiddleware, SLOW_REQUEST_THRESHOLD
from .correlation import (
    CorrelationIdMiddleware,
    CORRELATION_ID_HEADER,
    get_correlation_id_from_request,
    get_correlation_id_middleware
)
from .case_permission import (
    CasePermissionChecker,
    get_permission_checker,
    require_case_access,
    require_case_write_access,
    require_case_owner,
    require_case_access_or_admin,
    require_case_write_or_admin,
    require_case_owner_or_admin
)

__all__ = [
    "LEHException",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "register_exception_handlers",
    "SecurityHeadersMiddleware",
    "HTTPSRedirectMiddleware",
    "AuditLogMiddleware",
    "LatencyLoggingMiddleware",
    "SLOW_REQUEST_THRESHOLD",
    # Correlation ID middleware
    "CorrelationIdMiddleware",
    "CORRELATION_ID_HEADER",
    "get_correlation_id_from_request",
    "get_correlation_id_middleware",
    # Case permission utilities
    "CasePermissionChecker",
    "get_permission_checker",
    "require_case_access",
    "require_case_write_access",
    "require_case_owner",
    "require_case_access_or_admin",
    "require_case_write_or_admin",
    "require_case_owner_or_admin"
]
