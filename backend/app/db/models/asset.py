"""
Asset Models (US2 - 재산분할표)
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import AssetCategory, AssetOwnership, AssetNature


class Asset(Base):
    """
    Asset model for detailed property division tracking
    US2 - 재산분할표 (Asset Division Sheet)
    """
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: f"asset_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic info
    category = Column(StrEnumColumn(AssetCategory), nullable=False)
    ownership = Column(StrEnumColumn(AssetOwnership), nullable=False)
    nature = Column(StrEnumColumn(AssetNature), nullable=True, default=AssetNature.MARITAL)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Valuation
    current_value = Column(Integer, nullable=False)  # 현재 가치 (원)
    acquisition_value = Column(Integer, nullable=True)  # 취득 가치 (원)
    acquisition_date = Column(DateTime(timezone=True), nullable=True)
    valuation_date = Column(DateTime(timezone=True), nullable=True)
    valuation_source = Column(String(100), nullable=True)  # 감정기관 등

    # Division proposal
    division_ratio_plaintiff = Column(Integer, nullable=True, default=50)  # 원고 분할 비율 (0-100)
    division_ratio_defendant = Column(Integer, nullable=True, default=50)  # 피고 분할 비율 (0-100)
    proposed_allocation = Column(StrEnumColumn(AssetOwnership), nullable=True)  # 제안된 귀속자

    # Evidence link
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="assets")

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, value={self.current_value})>"


class AssetDivisionSummary(Base):
    """
    Asset division summary - calculated division result per case
    US2 - 재산분할표 계산 결과
    """
    __tablename__ = "asset_division_summaries"

    id = Column(String, primary_key=True, default=lambda: f"summary_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Division calculation results
    total_marital_assets = Column(Integer, default=0)     # 혼인 중 재산 총액
    total_separate_plaintiff = Column(Integer, default=0)  # 원고 특유재산
    total_separate_defendant = Column(Integer, default=0)  # 피고 특유재산
    total_debts = Column(Integer, default=0)              # 총 부채액
    net_marital_value = Column(Integer, default=0)        # 순 혼인재산 (자산-부채)

    # Calculated shares
    plaintiff_share = Column(Integer, default=0)          # 원고 분할액
    defendant_share = Column(Integer, default=0)          # 피고 분할액
    settlement_amount = Column(Integer, default=0)        # 정산금 (양수=원고→피고)

    # Current holdings
    plaintiff_holdings = Column(Integer, default=0)       # 원고 현재 보유액
    defendant_holdings = Column(Integer, default=0)       # 피고 현재 보유액

    # Calculation parameters
    plaintiff_ratio = Column(Integer, default=50)         # 원고 비율 (0-100)
    defendant_ratio = Column(Integer, default=50)         # 피고 비율 (0-100)

    # Legacy fields (backward compatibility)
    total_assets = Column(Integer, default=0)             # (legacy) 총 재산액
    net_value = Column(Integer, default=0)                # (legacy) 순자산
    plaintiff_assets = Column(Integer, default=0)         # (legacy)
    defendant_assets = Column(Integer, default=0)         # (legacy)
    joint_assets = Column(Integer, default=0)             # (legacy)
    category_breakdown = Column(JSON, nullable=True)      # (legacy)

    # Metadata
    notes = Column(Text, nullable=True)                   # 계산 메모
    calculated_by = Column(String, nullable=True)         # 계산 수행자

    # Timestamps
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="asset_division_summaries")

    def __repr__(self):
        return f"<AssetDivisionSummary(case_id={self.case_id}, settlement={self.settlement_amount})>"
