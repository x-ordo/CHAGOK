"""
Job Queue Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import JobStatus, JobType


# ============================================
# Job Queue Schemas
# ============================================
class JobCreate(BaseModel):
    """Job creation request schema"""
    case_id: str
    job_type: JobType
    evidence_id: Optional[str] = None
    parameters: Optional[dict] = None


class JobOut(BaseModel):
    """Job output schema"""
    id: str
    case_id: str
    user_id: str
    job_type: JobType
    status: JobStatus
    evidence_id: Optional[str] = None
    progress: int = 0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class JobDetail(BaseModel):
    """Job detail schema with full data"""
    id: str
    case_id: str
    user_id: str
    job_type: JobType
    status: JobStatus
    evidence_id: Optional[str] = None
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error_details: Optional[dict] = None
    progress: int = 0
    retry_count: int = 0
    max_retries: int = 3
    lambda_request_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Job list response schema"""
    jobs: List[JobOut]
    total: int


class JobStatusUpdate(BaseModel):
    """Job status update request (for callbacks)"""
    status: JobStatus
    output_data: Optional[dict] = None
    error_details: Optional[dict] = None
    lambda_request_id: Optional[str] = None


class JobProgressUpdate(BaseModel):
    """Job progress update request"""
    progress: int = Field(..., ge=0, le=100)
