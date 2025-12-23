"""
Detective Schemas - Investigation Records, Reports, Contacts
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import InvestigationRecordType


# ============================================
# Investigation Record Schemas
# ============================================
class InvestigationRecordCreate(BaseModel):
    """Investigation record creation request schema"""
    case_id: str
    record_type: InvestigationRecordType
    content: Optional[str] = None
    location_lat: Optional[str] = None
    location_lng: Optional[str] = None
    location_address: Optional[str] = None
    attachments: Optional[List[str]] = None
    recorded_at: datetime


class InvestigationRecordOut(BaseModel):
    """Investigation record output schema"""
    id: str
    case_id: str
    detective_id: str
    detective_name: Optional[str] = None
    record_type: InvestigationRecordType
    content: Optional[str] = None
    location_lat: Optional[str] = None
    location_lng: Optional[str] = None
    location_address: Optional[str] = None
    attachments: Optional[List[str]] = None
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class InvestigationRecordListResponse(BaseModel):
    """Investigation record list response schema"""
    records: List[InvestigationRecordOut]
    total: int


class InvestigationReportSubmit(BaseModel):
    """Investigation report submission schema"""
    case_id: str
    summary: str = Field(..., min_length=10)
    findings: str
    evidence_ids: List[str] = Field(default_factory=list)
    recommendations: Optional[str] = None


# ============================================
# Detective Contact Schemas (Issue #298 - FR-011~012, FR-016)
# ============================================
class DetectiveContactCreate(BaseModel):
    """Create detective contact request schema"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    specialty: Optional[str] = Field(None, max_length=100)
    memo: Optional[str] = None


class DetectiveContactUpdate(BaseModel):
    """Update detective contact request schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    specialty: Optional[str] = Field(None, max_length=100)
    memo: Optional[str] = None


class DetectiveContactResponse(BaseModel):
    """Detective contact response schema"""
    id: str
    lawyer_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    specialty: Optional[str] = None
    memo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DetectiveContactListResponse(BaseModel):
    """Detective contact list response schema"""
    items: List[DetectiveContactResponse]
    total: int
    page: int
    limit: int
