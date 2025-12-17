"""
Party Graph Schemas - Nodes, Relationships, Evidence Links
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import PartyType, RelationshipType, LinkType


# ============================================
# Party Graph Schemas (v1 Lawyer Portal)
# ============================================
class Position(BaseModel):
    """Position schema for React Flow coordinates"""
    x: float = 0
    y: float = 0


class PartyNodeCreate(BaseModel):
    """Create party node request schema"""
    type: PartyType
    name: str = Field(..., min_length=1, max_length=100)
    alias: Optional[str] = Field(None, max_length=50)
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    occupation: Optional[str] = Field(None, max_length=100)
    position: Position = Position()
    extra_data: Optional[dict] = None


class PartyNodeUpdate(BaseModel):
    """Update party node request schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    alias: Optional[str] = Field(None, max_length=50)
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    occupation: Optional[str] = Field(None, max_length=100)
    position: Optional[Position] = None
    extra_data: Optional[dict] = None


class PartyNodeResponse(BaseModel):
    """Party node response schema"""
    id: str
    case_id: str
    type: PartyType
    name: str
    alias: Optional[str] = None
    birth_year: Optional[int] = None
    occupation: Optional[str] = None
    position: Position
    extra_data: Optional[dict] = None
    # 012-precedent-integration: T036-T038 자동 추출 필드
    is_auto_extracted: bool = False
    extraction_confidence: Optional[float] = None
    source_evidence_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RelationshipCreate(BaseModel):
    """Create relationship request schema"""
    source_party_id: str
    target_party_id: str
    type: RelationshipType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class RelationshipUpdate(BaseModel):
    """Update relationship request schema"""
    type: Optional[RelationshipType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class RelationshipResponse(BaseModel):
    """Relationship response schema"""
    id: str
    case_id: str
    source_party_id: str
    target_party_id: str
    type: RelationshipType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    # 012-precedent-integration: T039 자동 추출 필드
    is_auto_extracted: bool = False
    extraction_confidence: Optional[float] = None
    evidence_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartyGraphResponse(BaseModel):
    """Combined party graph data response"""
    nodes: List[PartyNodeResponse]
    relationships: List[RelationshipResponse]


# ============================================
# 012-precedent-integration: T040-T043 자동 추출 스키마
# ============================================
class AutoExtractedPartyRequest(BaseModel):
    """AI Worker가 추출한 인물 저장 요청 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="인물 이름")
    type: PartyType = Field(..., description="인물 유형 (plaintiff, defendant, etc.)")
    extraction_confidence: float = Field(..., ge=0.0, le=1.0, description="추출 신뢰도")
    source_evidence_id: str = Field(..., description="추출 근거 증거 ID")
    alias: Optional[str] = Field(None, max_length=50)
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    occupation: Optional[str] = Field(None, max_length=100)


class AutoExtractedPartyResponse(BaseModel):
    """자동 추출 인물 저장 응답"""
    id: str
    name: str
    is_duplicate: bool = False
    matched_party_id: Optional[str] = None  # 중복 감지 시 기존 인물 ID


class AutoExtractedRelationshipRequest(BaseModel):
    """AI Worker가 추론한 관계 저장 요청 스키마"""
    source_party_id: str = Field(..., description="출발 인물 ID")
    target_party_id: str = Field(..., description="도착 인물 ID")
    type: RelationshipType = Field(..., description="관계 유형")
    extraction_confidence: float = Field(..., ge=0.7, le=1.0, description="추출 신뢰도 (최소 0.7)")
    evidence_text: Optional[str] = Field(None, max_length=500, description="관계 추론 근거 텍스트")


class AutoExtractedRelationshipResponse(BaseModel):
    """자동 추출 관계 저장 응답"""
    id: str
    created: bool


class EvidenceLinkCreate(BaseModel):
    """Create evidence-party link request schema"""
    evidence_id: str = Field(..., max_length=100)
    party_id: Optional[str] = None
    relationship_id: Optional[str] = None
    link_type: LinkType = LinkType.MENTIONS


class EvidenceLinkResponse(BaseModel):
    """Evidence-party link response schema"""
    id: str
    case_id: str
    evidence_id: str
    party_id: Optional[str] = None
    relationship_id: Optional[str] = None
    link_type: LinkType
    created_at: datetime

    class Config:
        from_attributes = True


class EvidenceLinksResponse(BaseModel):
    """List of evidence links response"""
    links: List[EvidenceLinkResponse]
    total: int
