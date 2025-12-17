"""
Dashboard Schemas - Stats, Portal Access
"""

from pydantic import BaseModel, Field
from typing import List
from app.db.models import UserRole


# ============================================
# Dashboard Schemas
# ============================================
class LawyerDashboardStats(BaseModel):
    """Lawyer dashboard statistics"""
    active_cases: int = 0
    pending_review: int = 0
    completed_cases: int = 0
    total_evidence: int = 0
    upcoming_events: int = 0
    unread_messages: int = 0


class ClientDashboardStats(BaseModel):
    """Client dashboard statistics"""
    total_cases: int = 0
    active_cases: int = 0
    pending_invoices: int = 0
    total_evidence: int = 0
    unread_messages: int = 0


class DetectiveDashboardStats(BaseModel):
    """Detective dashboard statistics"""
    assigned_cases: int = 0
    pending_cases: int = 0
    completed_cases: int = 0
    total_records: int = 0
    pending_reports: int = 0
    total_earnings: str = "0"  # Total earnings in KRW


# ============================================
# Role Permission Configuration
# ============================================
class PortalAccess(BaseModel):
    """Portal access configuration per role"""
    role: UserRole
    portal_path: str
    allowed_features: List[str]
    restricted_features: List[str] = Field(default_factory=list)


# Default role permissions configuration
ROLE_PORTAL_CONFIG = {
    UserRole.ADMIN: PortalAccess(
        role=UserRole.ADMIN,
        portal_path="/admin",
        allowed_features=["*"],  # All access
        restricted_features=[]
    ),
    UserRole.LAWYER: PortalAccess(
        role=UserRole.LAWYER,
        portal_path="/lawyer",
        allowed_features=[
            "dashboard", "cases", "evidence", "timeline", "draft",
            "clients", "investigators", "calendar", "billing", "messages"
        ],
        restricted_features=["admin"]
    ),
    UserRole.STAFF: PortalAccess(
        role=UserRole.STAFF,
        portal_path="/lawyer",  # Same as lawyer
        allowed_features=[
            "dashboard", "cases", "evidence", "timeline",
            "calendar", "messages"
        ],
        restricted_features=["admin", "billing", "draft"]
    ),
    UserRole.CLIENT: PortalAccess(
        role=UserRole.CLIENT,
        portal_path="/client",
        allowed_features=[
            "dashboard", "cases", "evidence", "timeline",
            "messages", "billing"
        ],
        restricted_features=["admin", "draft", "investigators"]
    ),
    UserRole.DETECTIVE: PortalAccess(
        role=UserRole.DETECTIVE,
        portal_path="/detective",
        allowed_features=[
            "dashboard", "cases", "field", "evidence", "report",
            "messages", "calendar", "earnings"
        ],
        restricted_features=["admin", "billing", "draft", "clients"]
    )
}
