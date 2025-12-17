"""
Messaging Schemas - Messages, Notifications
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import NotificationType


# ============================================
# Messaging Schemas (Legacy - for case-based messaging)
# ============================================
class MessageCreateLegacy(BaseModel):
    """Message creation request schema (case-based)"""
    case_id: str
    recipient_id: str
    content: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None  # List of attachment URLs


class MessageOut(BaseModel):
    """Message output schema"""
    id: str
    case_id: str
    sender_id: str
    sender_name: Optional[str] = None
    recipient_id: str
    recipient_name: Optional[str] = None
    content: str
    attachments: Optional[List[str]] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponseLegacy(BaseModel):
    """Message list response schema (case-based)"""
    messages: List[MessageOut]
    total: int
    unread_count: int = 0


class MarkMessageReadRequest(BaseModel):
    """Mark message as read request"""
    message_ids: List[str]


# ============================================
# Message Schemas (Issue #296 - FR-008)
# ============================================
class MessageCreate(BaseModel):
    """Create message request schema"""
    recipient_id: str
    subject: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=1)
    case_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Message response schema"""
    id: str
    sender_id: str
    recipient_id: str
    subject: Optional[str] = None
    content: str
    case_id: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    # Include sender/recipient info for convenience
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Message list response schema"""
    messages: List[MessageResponse]
    total: int
    page: int
    limit: int


# ============================================
# Notification Schemas (Issue #295 - FR-007)
# ============================================
class NotificationCreate(BaseModel):
    """Create notification request schema"""
    user_id: str
    type: NotificationType = NotificationType.SYSTEM
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=500)
    related_id: Optional[str] = None


class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: str
    user_id: str
    type: NotificationType
    title: str
    content: str
    is_read: bool
    related_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list response schema"""
    notifications: List[NotificationResponse]
    unread_count: int


class NotificationReadAllResponse(BaseModel):
    """Response for marking all notifications as read"""
    updated_count: int
