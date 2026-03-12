from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OffenderSearchRequest(BaseModel):
    last_name: Optional[str] = None
    first_name_initial: Optional[str] = None
    tdcj_number: Optional[str] = None
    sid: Optional[str] = None
    page: int = 1


class OffenderSearchResult(BaseModel):
    name: str
    sid: str
    tdcj_number: Optional[str] = None
    race: Optional[str] = None
    gender: Optional[str] = None
    projected_release_date: Optional[str] = None
    unit: Optional[str] = None
    age: Optional[int] = None
    detail_url: str


class OffenderSearchPagination(BaseModel):
    current_page: int
    total_pages: int
    has_more: bool


class OffenderSearchResponse(BaseModel):
    results: list[OffenderSearchResult]
    pagination: OffenderSearchPagination
    source: str
    retrieved_at: datetime


class OffenseHistoryEntry(BaseModel):
    offense_date: Optional[str] = None
    offense: Optional[str] = None
    sentence_date: Optional[str] = None
    county: Optional[str] = None
    case_number: Optional[str] = None
    sentence_length: Optional[str] = None


class OffenderDetailResponse(BaseModel):
    sid: str
    tdcj_number: Optional[str] = None
    name: Optional[str] = None
    race: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    maximum_sentence_date: Optional[str] = None
    current_facility: Optional[str] = None
    projected_release_date: Optional[str] = None
    parole_eligibility_date: Optional[str] = None
    visitation_eligible: Optional[bool] = None
    visitation_eligible_raw: Optional[str] = None
    scheduled_release_date_text: Optional[str] = None
    scheduled_release_type_text: Optional[str] = None
    scheduled_release_location_text: Optional[str] = None
    parole_review_url: Optional[str] = None
    offense_history: list[OffenseHistoryEntry]
    source: str
    retrieved_at: datetime
    source_note: str
