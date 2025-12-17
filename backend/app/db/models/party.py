"""
Party Graph Models (v1 Lawyer Portal)
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import PartyType, RelationshipType, LinkType


class PartyNode(Base):
    """
    Party node model - represents a person in the relationship graph
    원고, 피고, 제3자, 자녀, 친족 등 사건에 등장하는 인물
    """
    __tablename__ = "party_nodes"

    id = Column(String, primary_key=True, default=lambda: f"party_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(StrEnumColumn(PartyType), nullable=False)
    name = Column(String(100), nullable=False)
    alias = Column(String(50), nullable=True)  # 소장용 가명 (김○○)
    birth_year = Column(Integer, nullable=True)
    occupation = Column(String(100), nullable=True)
    position_x = Column(Integer, nullable=False, default=0)  # React Flow X coordinate
    position_y = Column(Integer, nullable=False, default=0)  # React Flow Y coordinate
    extra_data = Column(JSON, nullable=True, default=dict)  # Additional info (renamed from metadata)
    # 012-precedent-integration: T036-T038 자동 추출 필드
    is_auto_extracted = Column(Boolean, default=False, nullable=False)  # AI가 추출했는지 여부
    extraction_confidence = Column(Float, nullable=True)  # 추출 신뢰도 (0.0-1.0)
    source_evidence_id = Column(String, nullable=True)  # 추출 근거 증거 ID
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="party_nodes")
    source_relationships = relationship(
        "PartyRelationship",
        foreign_keys="PartyRelationship.source_party_id",
        back_populates="source_party",
        cascade="all, delete-orphan"
    )
    target_relationships = relationship(
        "PartyRelationship",
        foreign_keys="PartyRelationship.target_party_id",
        back_populates="target_party",
        cascade="all, delete-orphan"
    )
    evidence_links = relationship("EvidencePartyLink", back_populates="party", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PartyNode(id={self.id}, name={self.name}, type={self.type})>"


class PartyRelationship(Base):
    """
    Party relationship model - represents a connection between two parties
    혼인, 불륜, 부모-자녀, 형제자매, 인척, 동거 관계
    """
    __tablename__ = "party_relationships"

    id = Column(String, primary_key=True, default=lambda: f"rel_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    source_party_id = Column(String, ForeignKey("party_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_party_id = Column(String, ForeignKey("party_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(StrEnumColumn(RelationshipType), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)  # 관계 시작일
    end_date = Column(DateTime(timezone=True), nullable=True)    # 관계 종료일
    notes = Column(Text, nullable=True)
    # 012-precedent-integration: T039 자동 추출 필드
    is_auto_extracted = Column(Boolean, default=False, nullable=False)  # AI가 추출했는지 여부
    extraction_confidence = Column(Float, nullable=True)  # 추출 신뢰도 (0.0-1.0)
    evidence_text = Column(Text, nullable=True)  # 관계 추론 근거 텍스트
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="party_relationships")
    source_party = relationship(
        "PartyNode",
        foreign_keys=[source_party_id],
        back_populates="source_relationships"
    )
    target_party = relationship(
        "PartyNode",
        foreign_keys=[target_party_id],
        back_populates="target_relationships"
    )
    evidence_links = relationship("EvidencePartyLink", back_populates="relationship", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PartyRelationship(id={self.id}, type={self.type}, source={self.source_party_id}, target={self.target_party_id})>"


class EvidencePartyLink(Base):
    """
    Evidence-party link model - connects evidence to parties, relationships, or assets
    증거와 당사자/관계/자산 간의 연결
    """
    __tablename__ = "evidence_party_links"

    id = Column(String, primary_key=True, default=lambda: f"link_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(String(100), nullable=False, index=True)  # References DynamoDB evidence
    party_id = Column(String, ForeignKey("party_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    relationship_id = Column(String, ForeignKey("party_relationships.id", ondelete="CASCADE"), nullable=True, index=True)
    link_type = Column(StrEnumColumn(LinkType), nullable=False, default=LinkType.MENTIONS)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="evidence_party_links")
    party = relationship("PartyNode", back_populates="evidence_links")
    relationship = relationship("PartyRelationship", back_populates="evidence_links")

    def __repr__(self):
        return f"<EvidencePartyLink(id={self.id}, evidence_id={self.evidence_id}, link_type={self.link_type})>"
