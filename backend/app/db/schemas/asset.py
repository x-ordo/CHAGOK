"""
Asset Schemas (US2 - 재산분할표)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import AssetCategory, AssetOwnership, AssetNature


# ============================================
# Asset Schemas (US2 - 재산분할표)
# ============================================
class AssetCreate(BaseModel):
    """Asset creation schema"""
    category: AssetCategory
    ownership: AssetOwnership
    name: str = Field(..., max_length=255)
    current_value: int = Field(..., ge=0)
    nature: Optional[AssetNature] = AssetNature.MARITAL
    description: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    acquisition_value: Optional[int] = None
    valuation_date: Optional[datetime] = None
    valuation_source: Optional[str] = Field(None, max_length=100)
    division_ratio_plaintiff: Optional[int] = Field(50, ge=0, le=100)
    division_ratio_defendant: Optional[int] = Field(50, ge=0, le=100)
    proposed_allocation: Optional[AssetOwnership] = None
    evidence_id: Optional[str] = None
    notes: Optional[str] = None


class AssetUpdate(BaseModel):
    """Asset update schema"""
    category: Optional[AssetCategory] = None
    ownership: Optional[AssetOwnership] = None
    name: Optional[str] = Field(None, max_length=255)
    current_value: Optional[int] = Field(None, ge=0)
    nature: Optional[AssetNature] = None
    description: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    acquisition_value: Optional[int] = None
    valuation_date: Optional[datetime] = None
    valuation_source: Optional[str] = Field(None, max_length=100)
    division_ratio_plaintiff: Optional[int] = Field(None, ge=0, le=100)
    division_ratio_defendant: Optional[int] = Field(None, ge=0, le=100)
    proposed_allocation: Optional[AssetOwnership] = None
    evidence_id: Optional[str] = None
    notes: Optional[str] = None


class AssetResponse(BaseModel):
    """Asset response schema"""
    id: str
    case_id: str
    category: AssetCategory
    ownership: AssetOwnership
    nature: Optional[AssetNature] = None
    name: str
    description: Optional[str] = None
    current_value: int
    acquisition_value: Optional[int] = None
    acquisition_date: Optional[datetime] = None
    valuation_date: Optional[datetime] = None
    valuation_source: Optional[str] = None
    division_ratio_plaintiff: Optional[int] = None
    division_ratio_defendant: Optional[int] = None
    proposed_allocation: Optional[AssetOwnership] = None
    evidence_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Asset list response with pagination"""
    assets: List[AssetResponse]
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 1


class DivisionCalculateRequest(BaseModel):
    """Request to calculate property division"""
    plaintiff_ratio: int = Field(50, ge=0, le=100)
    defendant_ratio: int = Field(50, ge=0, le=100)
    include_separate: bool = Field(False, description="Whether to include separate property in division")
    notes: Optional[str] = Field(None, description="Additional notes for the calculation")


class AssetCategorySummary(BaseModel):
    """Summary for a single asset category"""
    category: AssetCategory
    total_value: int
    count: int
    plaintiff_value: int
    defendant_value: int
    joint_value: int


class DivisionSummaryResponse(BaseModel):
    """Division calculation summary response"""
    total_marital_assets: int
    total_separate_plaintiff: int = 0
    total_separate_defendant: int = 0
    total_debts: int
    net_marital_value: int
    plaintiff_share: int
    defendant_share: int
    settlement_amount: int
    plaintiff_holdings: int
    defendant_holdings: int
    # Additional metadata
    id: Optional[str] = None
    case_id: Optional[str] = None
    plaintiff_ratio: Optional[int] = None
    defendant_ratio: Optional[int] = None

    class Config:
        from_attributes = True


class AssetSheetSummary(BaseModel):
    """Complete asset sheet summary"""
    division_summary: Optional[DivisionSummaryResponse] = None
    category_summaries: List[AssetCategorySummary]
    total_assets: int
