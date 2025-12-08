"""
Lawyer Clients API Router
005-lawyer-portal-pages Feature - US2

API endpoints for lawyer's client management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user_id
from app.services.client_list_service import ClientListService
from app.schemas.client_list import (
    ClientListResponse,
    ClientDetail,
    ClientFilter,
    ClientSortField,
    SortOrder,
    ClientStatus,
)


router = APIRouter(prefix="/lawyer/clients", tags=["lawyer-clients"])


@router.get("", response_model=ClientListResponse)
async def get_clients(
    search: Optional[str] = Query(None, description="Search by name or email"),
    status: Optional[ClientStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: ClientSortField = Query(
        ClientSortField.NAME, description="Field to sort by"
    ),
    sort_order: SortOrder = Query(SortOrder.ASC, description="Sort order"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get list of lawyer's clients with filters and pagination.

    Clients are users with role='client' who are members of cases
    that the current lawyer has access to.
    """
    service = ClientListService(db)

    filters = ClientFilter(
        search=search,
        status=status,
    )

    return service.get_clients(
        lawyer_id=user_id,
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{client_id}", response_model=ClientDetail)
async def get_client_detail(
    client_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get detailed information for a specific client.

    Returns 404 if client is not found or lawyer doesn't have access.
    """
    service = ClientListService(db)

    client = service.get_client_detail(
        lawyer_id=user_id,
        client_id=client_id,
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found or access denied",
        )

    return client
