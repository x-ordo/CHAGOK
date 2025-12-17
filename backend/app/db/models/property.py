"""
Property & Division Prediction Models
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import PropertyType, PropertyOwner, ConfidenceLevel


class CaseProperty(Base):
    """
    Case property model - assets and debts for property division calculation
    재산분할 계산을 위한 사건별 재산/부채 정보
    """
    __tablename__ = "case_properties"

    id = Column(String, primary_key=True, default=lambda: f"prop_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    property_type = Column(StrEnumColumn(PropertyType), nullable=False)
    description = Column(String(255), nullable=True)
    estimated_value = Column(Integer, nullable=False)  # 원 단위 (BigInt for large values)
    owner = Column(StrEnumColumn(PropertyOwner), nullable=False, default=PropertyOwner.JOINT)
    is_premarital = Column(Boolean, default=False)  # 혼전 재산 여부 (분할 제외 가능)
    acquisition_date = Column(DateTime(timezone=True), nullable=True)  # 취득일
    notes = Column(Text, nullable=True)  # 추가 메모
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="properties")

    def __repr__(self):
        return f"<CaseProperty(id={self.id}, type={self.property_type}, value={self.estimated_value})>"


class DivisionPrediction(Base):
    """
    Division prediction model - AI-generated property division predictions
    AI 기반 재산분할 예측 결과 저장
    """
    __tablename__ = "division_predictions"

    id = Column(String, primary_key=True, default=lambda: f"pred_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # 총 재산 정보
    total_property_value = Column(Integer, nullable=False)  # 총 재산액 (원)
    total_debt_value = Column(Integer, default=0)  # 총 부채액 (원)
    net_value = Column(Integer, nullable=False)  # 순자산 (재산 - 부채)

    # 분할 비율
    plaintiff_ratio = Column(Integer, nullable=False)  # 원고 비율 (0-100)
    defendant_ratio = Column(Integer, nullable=False)  # 피고 비율 (0-100)
    plaintiff_amount = Column(Integer, nullable=False)  # 원고 예상 수령액
    defendant_amount = Column(Integer, nullable=False)  # 피고 예상 수령액

    # 분석 결과
    evidence_impacts = Column(JSON, nullable=True)  # 증거별 영향도 리스트
    similar_cases = Column(JSON, nullable=True)  # 유사 판례 리스트
    confidence_level = Column(StrEnumColumn(ConfidenceLevel), nullable=False, default=ConfidenceLevel.MEDIUM)

    # 메타
    version = Column(Integer, default=1)  # 예측 버전 (재계산 시 증가)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="predictions")

    def __repr__(self):
        return f"<DivisionPrediction(id={self.id}, ratio={self.plaintiff_ratio}:{self.defendant_ratio})>"
