"""
Messaging & Notification Models
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import NotificationType


class Message(Base):
    """
    Message model - real-time communication between users
    Updated for Issue #294, #296 - FR-008
    """
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id"), nullable=True, index=True)  # Optional case link
    sender_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String(200), nullable=True)  # Message subject
    content = Column(Text, nullable=False)
    attachments = Column(String, nullable=True)  # JSON string of attachment URLs
    is_read = Column(Boolean, nullable=False, default=False)
    is_deleted_by_sender = Column(Boolean, nullable=False, default=False)
    is_deleted_by_recipient = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>"


class Notification(Base):
    """
    Notification model - user notifications
    Issue #294, #295 - FR-007
    """
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: f"notif_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(StrEnumColumn(NotificationType), nullable=False, default=NotificationType.SYSTEM)
    title = Column(String(100), nullable=False)
    content = Column(String(500), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    related_id = Column(String, nullable=True)  # case_id, message_id, etc.
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"
