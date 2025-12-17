"""
Client Contact Model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base


class ClientContact(Base):
    """
    Client contact model - Lawyer's client contacts
    Issue #294, #297 - FR-009~010, FR-015
    """
    __tablename__ = "client_contacts"

    id = Column(String, primary_key=True, default=lambda: f"client_{uuid.uuid4().hex[:12]}")
    lawyer_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    lawyer = relationship("User", backref="client_contacts")

    def __repr__(self):
        return f"<ClientContact(id={self.id}, name={self.name}, lawyer_id={self.lawyer_id})>"
