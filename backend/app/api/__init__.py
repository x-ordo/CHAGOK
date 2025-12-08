"""
Legal Evidence Hub (LEH) - API Package
API endpoint routers (REST API endpoints)

Per BACKEND_SERVICE_REPOSITORY_GUIDE.md:
- API layer handles HTTP routing, request validation, and response wrapping
- Business logic delegated to services
- No direct DB or AWS SDK calls
"""

from . import auth
from . import cases
from . import evidence
from . import lawyer_portal
from . import settings

__all__ = ["auth", "cases", "evidence", "lawyer_portal", "settings"]
