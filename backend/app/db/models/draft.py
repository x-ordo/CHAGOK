"""
Draft Document Models
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import DocumentType, DraftStatus, ExportFormat, ExportJobStatus


class DraftDocument(Base):
    """
    Draft document model - AI-generated legal document drafts
    Linked to a case, can be edited and exported
    """
    __tablename__ = "draft_documents"

    id = Column(String, primary_key=True, default=lambda: f"draft_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    document_type = Column(StrEnumColumn(DocumentType), nullable=False, default=DocumentType.BRIEF)
    content = Column(JSON, nullable=False)  # Structured content with sections
    version = Column(Integer, nullable=False, default=1)
    status = Column(StrEnumColumn(DraftStatus), nullable=False, default=DraftStatus.DRAFT, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="draft_documents")
    creator = relationship("User", foreign_keys=[created_by])
    export_jobs = relationship("ExportJob", back_populates="draft", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DraftDocument(id={self.id}, title={self.title}, status={self.status})>"


class ExportJob(Base):
    """
    Export job model - tracks document export operations
    Used for audit trail and async export handling
    """
    __tablename__ = "export_jobs"

    id = Column(String, primary_key=True, default=lambda: f"export_{uuid.uuid4().hex[:12]}")
    draft_id = Column(String, ForeignKey("draft_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    format = Column(StrEnumColumn(ExportFormat), nullable=False)
    status = Column(StrEnumColumn(ExportJobStatus), nullable=False, default=ExportJobStatus.PENDING, index=True)
    file_key = Column(String(500), nullable=True)  # S3 key for generated file
    file_size = Column(Integer, nullable=True)  # File size in bytes
    page_count = Column(Integer, nullable=True)  # Number of pages
    error_message = Column(Text, nullable=True)  # Error details if failed
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # When S3 file expires

    # Relationships
    draft = relationship("DraftDocument", back_populates="export_jobs")
    case = relationship("Case", backref="export_jobs")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ExportJob(id={self.id}, format={self.format}, status={self.status})>"


class DocumentTemplate(Base):
    """
    Document template model - pre-configured legal document formatting templates
    """
    __tablename__ = "document_templates"

    id = Column(String, primary_key=True, default=lambda: f"template_{uuid.uuid4().hex[:12]}")
    name = Column(String(100), unique=True, nullable=False)
    document_type = Column(StrEnumColumn(DocumentType), nullable=False)
    description = Column(Text, nullable=True)
    html_template = Column(Text, nullable=False)  # Jinja2 HTML template for PDF
    css_styles = Column(Text, nullable=False)  # CSS for PDF formatting
    docx_template_key = Column(String(500), nullable=True)  # S3 key for Word template
    margins = Column(JSON, nullable=False, default=lambda: {"top": 25, "bottom": 25, "left": 20, "right": 20, "unit": "mm"})
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name={self.name}, document_type={self.document_type})>"
