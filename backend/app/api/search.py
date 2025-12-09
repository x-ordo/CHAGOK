"""
Search API - Global search endpoint
007-lawyer-portal-v1: US6 (Global Search)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user_id
from app.services.search_service import SearchService


router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def search(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    categories: Optional[str] = Query(
        None,
        description="Comma-separated list of categories: cases,clients,evidence,events"
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per category"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    글로벌 검색

    사건, 의뢰인, 증거, 일정을 통합 검색합니다.
    Cmd/Ctrl + K 단축키로 호출되는 검색 팔레트에서 사용됩니다.

    **검색 대상**:
    - **cases**: 사건 제목, 설명, 의뢰인명
    - **clients**: 의뢰인 이름, 이메일
    - **evidence**: 파일명, AI 요약, 레이블
    - **events**: 일정 제목, 설명, 장소

    **접근 제어**:
    - 사용자가 접근 가능한 케이스의 데이터만 검색됩니다.

    Args:
        q: 검색어 (최소 2자)
        categories: 검색 카테고리 (쉼표 구분, 선택 사항)
        limit: 카테고리별 최대 결과 수

    Returns:
        검색 결과 목록
    """
    service = SearchService(db)

    # Parse categories if provided
    category_list = None
    if categories:
        category_list = [c.strip() for c in categories.split(",") if c.strip()]

    result = service.search(
        query=q,
        user_id=user_id,
        categories=category_list,
        limit=limit
    )

    return result


@router.get("/quick-access")
async def get_quick_access(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    바로가기 정보 조회

    검색 팔레트의 바로가기 섹션에 표시할 정보를 반환합니다.
    - 오늘의 일정
    - 이번 주 마감 사건

    Returns:
        바로가기 정보
    """
    service = SearchService(db)
    return service.get_quick_access(user_id)


@router.get("/recent")
async def get_recent_searches(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    최근 검색어 조회

    사용자의 최근 검색 기록을 반환합니다.

    Args:
        limit: 최대 결과 수

    Returns:
        최근 검색어 목록
    """
    service = SearchService(db)
    return {"recent_searches": service.get_recent_searches(user_id, limit)}
