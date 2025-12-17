"""
User Settings Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.db.models import NotificationFrequency, ProfileVisibility


# ============================================
# User Settings Schemas
# ============================================
class ProfileSettingsUpdate(BaseModel):
    """Profile settings update request"""
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)


class NotificationSettingsUpdate(BaseModel):
    """Notification settings update request"""
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    notification_frequency: Optional[NotificationFrequency] = None


class PrivacySettingsUpdate(BaseModel):
    """Privacy settings update request"""
    profile_visibility: Optional[ProfileVisibility] = None


class SecuritySettingsUpdate(BaseModel):
    """Security settings update request"""
    two_factor_enabled: Optional[bool] = None


class ProfileSettingsOut(BaseModel):
    """Profile settings output schema"""
    display_name: Optional[str] = None
    email: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "Asia/Seoul"
    language: str = "ko"

    class Config:
        from_attributes = True


class NotificationSettingsOut(BaseModel):
    """Notification settings output schema"""
    email_enabled: bool = True
    push_enabled: bool = True
    frequency: NotificationFrequency = NotificationFrequency.IMMEDIATE

    class Config:
        from_attributes = True


class SecuritySettingsOut(BaseModel):
    """Security settings output schema"""
    two_factor_enabled: bool = False
    last_password_change: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSettingsResponse(BaseModel):
    """Complete user settings response"""
    profile: ProfileSettingsOut
    notifications: NotificationSettingsOut
    security: SecuritySettingsOut

    class Config:
        from_attributes = True


class SettingsUpdateRequest(BaseModel):
    """Combined settings update request"""
    profile: Optional[ProfileSettingsUpdate] = None
    notifications: Optional[NotificationSettingsUpdate] = None
    privacy: Optional[PrivacySettingsUpdate] = None
    security: Optional[SecuritySettingsUpdate] = None
