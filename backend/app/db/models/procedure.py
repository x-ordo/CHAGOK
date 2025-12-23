"""
Procedure Stage Model (US3)
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import ProcedureStageType, StageStatus


class ProcedureStageRecord(Base):
    """
    Procedure stage record - tracks the progress of a divorce case through stages
    이혼 사건의 단계별 진행 상황 기록
    """
    __tablename__ = "procedure_stage_records"

    id = Column(String, primary_key=True, default=lambda: f"stage_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Stage info
    stage = Column(StrEnumColumn(ProcedureStageType), nullable=False)
    status = Column(StrEnumColumn(StageStatus), nullable=False, default=StageStatus.PENDING)
    order_index = Column(Integer, nullable=False, default=0)  # Display order

    # Dates
    scheduled_date = Column(DateTime(timezone=True), nullable=True)  # 예정일
    started_at = Column(DateTime(timezone=True), nullable=True)      # 시작일
    completed_at = Column(DateTime(timezone=True), nullable=True)    # 완료일 (legacy)
    completed_date = Column(DateTime(timezone=True), nullable=True)  # 완료일

    # Court info
    court_reference = Column(String(100), nullable=True)  # 사건번호
    judge_name = Column(String(50), nullable=True)        # 담당 판사
    court_room = Column(String(50), nullable=True)        # 법정

    # Details
    notes = Column(Text, nullable=True)
    documents = Column(JSON, nullable=True, default=list)  # Related document IDs
    outcome = Column(String(100), nullable=True)          # 결과

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String, nullable=True)  # 작성자 ID

    # Relationships
    case = relationship("Case", backref=backref("procedure_stages", passive_deletes=True))

    def __repr__(self):
        return f"<ProcedureStageRecord(id={self.id}, stage={self.stage}, status={self.status})>"
