"""
Lawyer Investigators API Router
005-lawyer-portal-pages Feature - US3

API endpoints for lawyer's investigator management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user_id
from app.services.investigator_list_service import InvestigatorListService
from app.schemas.investigator_list import (
    InvestigatorListResponse,
    InvestigatorDetail,
    InvestigatorFilter,
    InvestigatorSortField,
    SortOrder,
    AvailabilityStatus,
)


router = APIRouter(prefix="/lawyer/investigators", tags=["lawyer-investigators"])


@router.get("", response_model=InvestigatorListResponse)
async def get_investigators(
    search: Optional[str] = Query(None, description="Search by name or email"),
    availability: Optional[AvailabilityStatus] = Query(
        None, description="Filter by availability"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: InvestigatorSortField = Query(
        InvestigatorSortField.NAME, description="Field to sort by"
    ),
    sort_order: SortOrder = Query(SortOrder.ASC, description="Sort order"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get list of lawyer's investigators with filters and pagination.

    Investigators are users with role='detective' who are members of cases
    that the current lawyer has access to.
    """
    service = InvestigatorListService(db)

    filters = InvestigatorFilter(
        search=search,
        availability=availability,
    )

    return service.get_investigators(
        lawyer_id=user_id,
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{investigator_id}", response_model=InvestigatorDetail)
async def get_investigator_detail(
    investigator_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get detailed information for a specific investigator.

    Returns 404 if investigator is not found or lawyer doesn't have access.
    """
    service = InvestigatorListService(db)

    investigator = service.get_investigator_detail(
        lawyer_id=user_id,
        investigator_id=investigator_id,
    )

    if not investigator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigator not found or access denied",
        )

    return investigator
