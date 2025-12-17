"""
User Settings Model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.models.base import Base
from app.db.models.enums import NotificationFrequency, ProfileVisibility


class UserSettings(Base):
    """
    User settings model - stores user preferences and notification settings
    """
    __tablename__ = "user_settings"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # Profile settings
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), nullable=False, default="Asia/Seoul")
    language = Column(String(10), nullable=False, default="ko")

    # Notification settings
    email_notifications = Column(Boolean, nullable=False, default=True)
    push_notifications = Column(Boolean, nullable=False, default=True)
    notification_frequency = Column(
        SQLEnum(NotificationFrequency),
        nullable=False,
        default=NotificationFrequency.IMMEDIATE
    )

    # Privacy settings
    profile_visibility = Column(
        SQLEnum(ProfileVisibility),
        nullable=False,
        default=ProfileVisibility.TEAM
    )

    # Security settings
    two_factor_enabled = Column(Boolean, nullable=False, default=False)
    last_password_change = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    user = relationship("User", backref="settings")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, language={self.language})>"
