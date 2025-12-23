"""
Calendar Event Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import CalendarEventType


# ============================================
# Calendar Event Schemas
# ============================================
class CalendarEventCreate(BaseModel):
    """Calendar event creation request schema"""
    case_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: CalendarEventType = CalendarEventType.OTHER
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    reminder_minutes: int = 30


class CalendarEventUpdate(BaseModel):
    """Calendar event update request schema"""
    case_id: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: Optional[CalendarEventType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    reminder_minutes: Optional[int] = None


class CalendarEventOut(BaseModel):
    """Calendar event output schema"""
    id: str
    user_id: str
    case_id: Optional[str] = None
    case_title: Optional[str] = None  # Joined from Case table
    title: str
    description: Optional[str] = None
    event_type: CalendarEventType
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    reminder_minutes: int
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarEventListResponse(BaseModel):
    """Calendar event list response schema"""
    events: List[CalendarEventOut]
    total: int
