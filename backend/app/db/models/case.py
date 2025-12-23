"""
Case Models
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import CaseStatus, CaseMemberRole


class Case(Base):
    """
    Case model - divorce cases
    Supports soft delete via deleted_at field
    """
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=lambda: f"case_{uuid.uuid4().hex[:12]}")
    title = Column(String, nullable=False)
    client_name = Column(String, nullable=True)  # 의뢰인 이름
    description = Column(String, nullable=True)
    status = Column(StrEnumColumn(CaseStatus), nullable=False, default=CaseStatus.ACTIVE)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)  # Soft delete timestamp

    # Relationships
    owner = relationship("User", back_populates="created_cases", foreign_keys=[created_by])
    members = relationship("CaseMember", back_populates="case", cascade="all, delete-orphan")

    @property
    def is_deleted(self) -> bool:
        """Check if case is soft deleted"""
        return self.deleted_at is not None

    def __repr__(self):
        return f"<Case(id={self.id}, title={self.title}, status={self.status}, deleted={self.is_deleted})>"


class CaseMember(Base):
    """
    Case membership model - user access to cases
    """
    __tablename__ = "case_members"

    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    role = Column(StrEnumColumn(CaseMemberRole), nullable=False, default=CaseMemberRole.VIEWER)

    # Relationships
    case = relationship("Case", back_populates="members")
    user = relationship("User", back_populates="case_memberships")

    def __repr__(self):
        return f"<CaseMember(case_id={self.case_id}, user_id={self.user_id}, role={self.role})>"


class CaseChecklistStatus(Base):
    """Tracks per-case completion state for mid-demo feedback checklist."""

    __tablename__ = "case_checklist_statuses"
    __table_args__ = (UniqueConstraint("case_id", "item_id", name="uq_case_checklist_item"),)

    id = Column(String, primary_key=True, default=lambda: f"cfbk_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    notes = Column(Text, nullable=True)
    updated_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    case = relationship("Case", backref="checklist_statuses")
    updater = relationship("User")

    def __repr__(self):
        return f"<CaseChecklistStatus(case_id={self.case_id}, item_id={self.item_id}, status={self.status})>"
