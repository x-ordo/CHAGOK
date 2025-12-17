"""
Property Division Schemas - Properties, Predictions
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import PropertyType, PropertyOwner, ConfidenceLevel


# ============================================
# Property Division Schemas (재산분할)
# ============================================
class PropertyCreate(BaseModel):
    """Property creation request schema"""
    property_type: PropertyType
    description: Optional[str] = Field(None, max_length=255)
    estimated_value: int = Field(..., ge=0, description="Estimated value in KRW")
    owner: PropertyOwner = PropertyOwner.JOINT
    is_premarital: bool = False
    acquisition_date: Optional[datetime] = None
    notes: Optional[str] = None


class PropertyUpdate(BaseModel):
    """Property update request schema"""
    property_type: Optional[PropertyType] = None
    description: Optional[str] = Field(None, max_length=255)
    estimated_value: Optional[int] = Field(None, ge=0)
    owner: Optional[PropertyOwner] = None
    is_premarital: Optional[bool] = None
    acquisition_date: Optional[datetime] = None
    notes: Optional[str] = None


class PropertyOut(BaseModel):
    """Property output schema"""
    id: str
    case_id: str
    property_type: PropertyType
    description: Optional[str] = None
    estimated_value: int
    owner: PropertyOwner
    is_premarital: bool
    acquisition_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyListResponse(BaseModel):
    """Property list response schema"""
    properties: List[PropertyOut]
    total: int
    total_assets: int = 0  # Sum of all positive values
    total_debts: int = 0   # Sum of all debt values
    net_value: int = 0     # Assets - Debts


class PropertySummary(BaseModel):
    """Property summary for dashboard"""
    total_assets: int
    total_debts: int
    net_value: int
    by_type: dict  # {property_type: total_value}
    by_owner: dict  # {owner: total_value}


# ============================================
# Division Prediction Schemas (재산분할 예측)
# ============================================
class EvidenceImpact(BaseModel):
    """Single evidence impact on division"""
    evidence_id: str
    evidence_type: str  # 'chat_log', 'photo', etc.
    impact_type: str    # 'adultery', 'violence', etc.
    impact_percent: float
    direction: str      # 'plaintiff_favor', 'defendant_favor', 'neutral'
    reason: str
    confidence: float = 0.8


class SimilarCase(BaseModel):
    """Similar precedent case"""
    case_ref: str       # e.g., "서울가정법원 2023드합1234"
    similarity_score: float
    division_ratio: str  # e.g., "60:40"
    key_factors: List[str] = Field(default_factory=list)


class DivisionPredictionOut(BaseModel):
    """Division prediction output schema"""
    id: str
    case_id: str
    total_property_value: int
    total_debt_value: int
    net_value: int
    plaintiff_ratio: int  # 0-100
    defendant_ratio: int  # 0-100
    plaintiff_amount: int
    defendant_amount: int
    evidence_impacts: List[EvidenceImpact] = Field(default_factory=list)
    similar_cases: List[SimilarCase] = Field(default_factory=list)
    confidence_level: ConfidenceLevel
    version: int
    created_at: datetime
    updated_at: datetime
    disclaimer: str = "본 예측은 참고용이며 실제 판결과 다를 수 있습니다."

    class Config:
        from_attributes = True


class DivisionPredictionRequest(BaseModel):
    """Request to trigger new prediction calculation"""
    force_recalculate: bool = False  # Force recalculation even if recent prediction exists
