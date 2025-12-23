"""
Detective & Investigation Models
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import InvestigationRecordType, EarningsStatus


class InvestigationRecord(Base):
    """
    Investigation record model - for detective field recordings
    GPS tracking, photos, memos, evidence collection
    """
    __tablename__ = "investigation_records"

    id = Column(String, primary_key=True, default=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    detective_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    record_type = Column(StrEnumColumn(InvestigationRecordType), nullable=False)
    content = Column(String, nullable=True)  # Text content or description
    location_lat = Column(String, nullable=True)  # Latitude
    location_lng = Column(String, nullable=True)  # Longitude
    location_address = Column(String, nullable=True)
    attachments = Column(String, nullable=True)  # JSON string of file URLs
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case")
    detective = relationship("User")

    def __repr__(self):
        return f"<InvestigationRecord(id={self.id}, type={self.record_type}, case_id={self.case_id})>"


class DetectiveEarnings(Base):
    """
    Detective earnings model - tracks detective payments per case
    탐정 정산 데이터 관리 (FR-040)
    """
    __tablename__ = "detective_earnings"

    id = Column(String, primary_key=True, default=lambda: f"earn_{uuid.uuid4().hex[:12]}")
    detective_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Payment info
    amount = Column(Integer, nullable=False)  # 금액 (원 단위)
    description = Column(String(500), nullable=True)  # 정산 내역 설명

    # Status
    status = Column(StrEnumColumn(EarningsStatus), nullable=False, default=EarningsStatus.PENDING, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)  # 정산 완료일

    # Relationships
    detective = relationship("User", foreign_keys=[detective_id])
    case = relationship("Case", backref="detective_earnings")

    def __repr__(self):
        return f"<DetectiveEarnings(id={self.id}, detective_id={self.detective_id}, amount={self.amount}, status={self.status})>"


class DetectiveContact(Base):
    """
    Detective contact model - Lawyer's detective contacts
    Issue #294, #298 - FR-011~012, FR-016
    """
    __tablename__ = "detective_contacts"

    id = Column(String, primary_key=True, default=lambda: f"det_{uuid.uuid4().hex[:12]}")
    lawyer_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    specialty = Column(String(100), nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    lawyer = relationship("User", backref="detective_contacts")

    def __repr__(self):
        return f"<DetectiveContact(id={self.id}, name={self.name}, specialty={self.specialty})>"
