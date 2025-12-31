"""
Users API endpoints - Privacy and personal data management
GDPR/PIPA compliance endpoints for personal data access and deletion

GET /users/me/data - Get all personal data (PIPA Article 35)
DELETE /users/me/data - Request personal data deletion (PIPA Article 36)
GET /users/me/activity - Get activity log
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.schemas import UserOut
from app.core.dependencies import get_current_user_id
from app.repositories.user_repository import UserRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.audit_log_repository import AuditLogRepository


router = APIRouter()


# ============================================
# Response Schemas
# ============================================
class ActivityLogEntry(BaseModel):
    """Single activity log entry"""
    id: str
    action: str
    object_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class CaseSummary(BaseModel):
    """Minimal case information for privacy export"""
    id: str
    title: str
    status: str
    role: str  # OWNER, MEMBER, VIEWER
    created_at: datetime


class PersonalDataExport(BaseModel):
    """
    Comprehensive personal data export for GDPR/PIPA compliance.
    Contains all data associated with a user.
    """
    # Basic user info
    user: UserOut

    # Cases the user is associated with
    cases: List[CaseSummary]

    # Activity log (last 90 days by default)
    activity_log: List[ActivityLogEntry]

    # Metadata
    export_timestamp: datetime
    data_categories: List[str]

    class Config:
        from_attributes = True


# ============================================
# Endpoints
# ============================================
@router.get("/me/data", response_model=PersonalDataExport, status_code=status.HTTP_200_OK)
def get_personal_data(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all personal data associated with the current user.

    **PIPA Article 35 Compliance:**
    This endpoint allows users to access all personal data stored about them.

    **Response:**
    - User profile information
    - Cases the user is associated with
    - Activity log (last 90 days)
    - Data categories summary

    **Note:**
    - This is a read-only operation
    - Large datasets may take time to compile
    - Sensitive data (passwords) is never included
    """
    user_repo = UserRepository(db)
    case_repo = CaseRepository(db)
    audit_repo = AuditLogRepository(db)

    # Get user info
    user = user_repo.get_by_id(user_id)
    if not user:
        from app.middleware.error_handler import NotFoundError
        raise NotFoundError("User not found")

    user_out = UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        status=user.status,
        created_at=user.created_at
    )

    # Get cases the user is associated with
    cases = case_repo.get_user_cases(user_id)
    case_summaries = []
    for case, role in cases:
        case_summaries.append(CaseSummary(
            id=case.id,
            title=case.title,
            status=case.status.value if hasattr(case.status, 'value') else str(case.status),
            role=role,
            created_at=case.created_at
        ))

    # Get activity log (last 90 days)
    activity_entries = audit_repo.get_user_activity(user_id, days=90)
    activity_log = []
    for entry in activity_entries:
        activity_log.append(ActivityLogEntry(
            id=entry.id,
            action=entry.action if isinstance(entry.action, str) else str(entry.action),
            object_id=entry.object_id,
            timestamp=entry.timestamp
        ))

    # Data categories summary
    data_categories = [
        "계정 정보 (이메일, 이름, 역할)",
        "사건 참여 기록",
        "활동 로그",
        "인증 정보 (암호화됨)"
    ]

    return PersonalDataExport(
        user=user_out,
        cases=case_summaries,
        activity_log=activity_log,
        export_timestamp=datetime.utcnow(),
        data_categories=data_categories
    )


@router.get("/me/activity", response_model=List[ActivityLogEntry], status_code=status.HTTP_200_OK)
def get_activity_log(
    days: int = 30,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get user activity log.

    **Query Parameters:**
    - days: Number of days to look back (default: 30, max: 365)
    - limit: Maximum number of entries (default: 100, max: 1000)

    **Response:**
    - List of activity log entries

    **Note:**
    - Only shows actions performed by the current user
    - Ordered by timestamp (newest first)
    """
    # Validate parameters
    days = min(max(days, 1), 365)
    limit = min(max(limit, 1), 1000)

    audit_repo = AuditLogRepository(db)
    activity_entries = audit_repo.get_user_activity(user_id, days=days, limit=limit)

    return [
        ActivityLogEntry(
            id=entry.id,
            action=entry.action if isinstance(entry.action, str) else str(entry.action),
            object_id=entry.object_id,
            timestamp=entry.timestamp
        )
        for entry in activity_entries
    ]


# ============================================
# Data Deletion Request Schemas
# ============================================
class DataDeletionRequest(BaseModel):
    """Data deletion request input"""
    reason: Optional[str] = None
    confirm: bool = False  # Must be True to proceed


class DataDeletionResponse(BaseModel):
    """Data deletion request response"""
    request_id: str
    status: str  # PENDING, SCHEDULED, COMPLETED
    scheduled_deletion_date: datetime
    message: str
    affected_data: List[str]


@router.delete("/me/data", response_model=DataDeletionResponse, status_code=status.HTTP_202_ACCEPTED)
def request_data_deletion(
    request: DataDeletionRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Request personal data deletion (PIPA Article 36).

    **PIPA Article 36 Compliance:**
    Users have the right to request deletion of their personal data.
    Deletion is scheduled after a 30-day grace period.

    **Request Body:**
    - reason: Optional reason for deletion
    - confirm: Must be True to proceed with deletion

    **Response:**
    - request_id: Unique deletion request ID
    - status: Request status (PENDING → SCHEDULED → COMPLETED)
    - scheduled_deletion_date: Date when data will be permanently deleted
    - affected_data: List of data categories that will be deleted

    **Process:**
    1. User submits deletion request (confirm=True)
    2. Account is immediately deactivated (soft delete)
    3. Data is scheduled for permanent deletion after 30 days
    4. User can cancel within 30-day grace period by contacting support

    **Note:**
    - This action cannot be undone after the grace period
    - User will be logged out immediately
    - Some data may be retained for legal compliance
    """
    from datetime import timedelta
    import uuid

    from app.middleware.error_handler import ValidationError

    if not request.confirm:
        raise ValidationError(
            "데이터 삭제를 진행하려면 confirm=True를 설정해야 합니다. "
            "이 작업은 되돌릴 수 없습니다."
        )

    user_repo = UserRepository(db)
    case_repo = CaseRepository(db)

    # Get user
    user = user_repo.get_by_id(user_id)
    if not user:
        from app.middleware.error_handler import NotFoundError
        raise NotFoundError("User not found")

    # Generate deletion request ID
    request_id = f"del_{uuid.uuid4().hex[:12]}"

    # Calculate scheduled deletion date (30 days from now)
    scheduled_date = datetime.utcnow() + timedelta(days=30)

    # Get affected data summary
    user_cases = case_repo.get_user_cases(user_id)
    affected_data = [
        "계정 정보 (이메일, 이름, 역할)",
        "인증 정보 (암호화된 비밀번호)",
        "활동 로그",
    ]
    if user_cases:
        affected_data.append(f"사건 참여 기록 ({len(user_cases)}건)")

    # Soft delete user (deactivate account)
    user_repo.soft_delete(user_id)

    # Create audit log for deletion request
    audit_repo = AuditLogRepository(db)
    audit_repo.create(
        user_id=user_id,
        action="DATA_DELETION_REQUESTED",
        object_id=request_id
    )

    db.commit()

    return DataDeletionResponse(
        request_id=request_id,
        status="SCHEDULED",
        scheduled_deletion_date=scheduled_date,
        message=(
            "데이터 삭제 요청이 접수되었습니다. "
            f"계정이 비활성화되었으며, {scheduled_date.strftime('%Y-%m-%d')}에 데이터가 영구 삭제됩니다. "
            "삭제를 취소하려면 30일 이내에 고객지원에 문의하세요."
        ),
        affected_data=affected_data
    )


@router.get("/me/deletion-status", response_model=DataDeletionResponse, status_code=status.HTTP_200_OK)
def get_deletion_status(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Check status of data deletion request.

    **Response:**
    - Current deletion request status
    - Scheduled deletion date
    - Affected data categories

    **Note:**
    This endpoint is available during the 30-day grace period.
    """
    from datetime import timedelta

    user_repo = UserRepository(db)
    audit_repo = AuditLogRepository(db)

    # Get user (including soft-deleted)
    user = user_repo.get_by_id(user_id)
    if not user:
        from app.middleware.error_handler import NotFoundError
        raise NotFoundError("User not found")

    # Check for deletion request in audit log
    # Get recent deletion request
    deletion_logs = [
        log for log in audit_repo.get_user_activity(user_id, days=30, limit=10)
        if log.action == "DATA_DELETION_REQUESTED"
    ]

    if not deletion_logs:
        from app.middleware.error_handler import NotFoundError
        raise NotFoundError("삭제 요청이 없습니다.")

    latest_request = deletion_logs[0]
    request_id = latest_request.object_id or f"del_{latest_request.id[:12]}"

    # Calculate scheduled deletion date (30 days from request)
    scheduled_date = latest_request.timestamp + timedelta(days=30)

    # Determine status
    now = datetime.utcnow()
    if now >= scheduled_date:
        status_str = "COMPLETED"
    else:
        status_str = "SCHEDULED"

    case_repo = CaseRepository(db)
    user_cases = case_repo.get_user_cases(user_id)
    affected_data = [
        "계정 정보 (이메일, 이름, 역할)",
        "인증 정보 (암호화된 비밀번호)",
        "활동 로그",
    ]
    if user_cases:
        affected_data.append(f"사건 참여 기록 ({len(user_cases)}건)")

    return DataDeletionResponse(
        request_id=request_id,
        status=status_str,
        scheduled_deletion_date=scheduled_date,
        message=(
            f"데이터 삭제가 {scheduled_date.strftime('%Y-%m-%d')}에 예정되어 있습니다."
            if status_str == "SCHEDULED"
            else "데이터 삭제가 완료되었습니다."
        ),
        affected_data=affected_data
    )
