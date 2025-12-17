"""
Client Contact Schemas (Issue #297 - FR-009~010, FR-015)
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# Client Contact Schemas
# ============================================
class ClientContactCreate(BaseModel):
    """Create client contact request schema"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    memo: Optional[str] = None


class ClientContactUpdate(BaseModel):
    """Update client contact request schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    memo: Optional[str] = None


class ClientContactResponse(BaseModel):
    """Client contact response schema"""
    id: str
    lawyer_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    memo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientContactListResponse(BaseModel):
    """Client contact list response schema"""
    items: List[ClientContactResponse]
    total: int
    page: int
    limit: int
