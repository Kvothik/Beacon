from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.core.security import require_authenticated_user
from backend.app.schemas.offender import OffenderDetailResponse, OffenderSearchRequest, OffenderSearchResponse
from backend.app.services.tdcj_lookup_service import SearchRequest, TdcjLookupService

router = APIRouter(prefix="/offenders", tags=["offenders"], dependencies=[Depends(require_authenticated_user)])


def get_tdcj_lookup_service() -> TdcjLookupService:
    return TdcjLookupService()


@router.post("/search", response_model=OffenderSearchResponse)
def search_offenders(
    payload: OffenderSearchRequest,
    service: TdcjLookupService = Depends(get_tdcj_lookup_service),
) -> OffenderSearchResponse:
    result = service.search_offenders(
        SearchRequest(
            last_name=payload.last_name,
            first_name_initial=payload.first_name_initial,
            tdcj_number=payload.tdcj_number,
            sid=payload.sid,
            page=payload.page,
        )
    )
    return OffenderSearchResponse(**result)


@router.get("/{sid}", response_model=OffenderDetailResponse)
def read_offender_detail(
    sid: str,
    service: TdcjLookupService = Depends(get_tdcj_lookup_service),
) -> OffenderDetailResponse:
    result = service.get_offender_detail(sid)
    return OffenderDetailResponse(**result)
