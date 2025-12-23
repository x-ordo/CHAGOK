"""
Evidence Model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base


class Evidence(Base):
    """
    Evidence model - uploaded evidence files for cases
    Metadata is stored here, actual files in S3, AI analysis results in DynamoDB/Qdrant
    """
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)

    # File info
    file_name = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    file_type = Column(String, nullable=True)  # MIME type
    file_size = Column(String, nullable=True)  # Size in bytes (stored as string for SQLite compatibility)
    description = Column(String, nullable=True)

    # Processing status
    status = Column(String, nullable=False, default="pending")  # pending, uploaded, processing, completed, failed

    # AI analysis results (stored as JSON strings for SQLite compatibility)
    ai_labels = Column(String, nullable=True)  # JSON array: ["폭언", "불륜", ...]
    ai_summary = Column(String, nullable=True)  # AI-generated summary
    ai_score = Column(String, nullable=True)  # Evidence strength score

    # Upload tracking
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="evidence_items")
    uploader = relationship("User")

    @property
    def ai_labels_list(self) -> list:
        """Parse ai_labels JSON string to list"""
        import json
        if not self.ai_labels:
            return []
        try:
            return json.loads(self.ai_labels)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self):
        return f"<Evidence(id={self.id}, file_name={self.file_name}, status={self.status})>"
