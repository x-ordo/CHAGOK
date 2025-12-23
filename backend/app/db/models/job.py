"""
Job Queue Model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import JobType, JobStatus


class Job(Base):
    """
    Job model - tracks async processing tasks (OCR, STT, draft generation, etc.)
    """
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: f"job_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    job_type = Column(StrEnumColumn(JobType), nullable=False)
    status = Column(StrEnumColumn(JobStatus), nullable=False, default=JobStatus.QUEUED)

    # Related resources
    evidence_id = Column(String, nullable=True, index=True)  # For evidence-related jobs

    # Job data (stored as JSON strings)
    input_data = Column(String, nullable=True)   # JSON: {s3_key, file_type, parameters, ...}
    output_data = Column(String, nullable=True)  # JSON: Result from AI processing
    error_details = Column(String, nullable=True)  # JSON: {error_code, message, traceback, ...}

    # Progress tracking
    progress = Column(String, default="0")  # 0-100 for long-running jobs

    # Retry tracking
    retry_count = Column(String, default="0")
    max_retries = Column(String, default="3")

    # AWS Lambda correlation
    lambda_request_id = Column(String, nullable=True)  # For CloudWatch logs correlation

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    case = relationship("Case")
    user = relationship("User")

    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"
