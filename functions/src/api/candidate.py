from __future__ import annotations

from fastapi import Depends, APIRouter, HTTPException

from src.models.candidate import (
    CompareRequest,
    BackgroundReport,
    ComparisonResult,
    CandidateSearchRequest,
    CandidateSearchResponse,
)
from src.services.candidate_service import CandidateService

router = APIRouter(prefix="/candidate", tags=["candidate"])


def get_candidate_service() -> CandidateService:
    """Execute get_candidate_service operation."""
    return CandidateService()


@router.post("/search", response_model=CandidateSearchResponse)
async def search_candidates(
    request: CandidateSearchRequest,
    service: CandidateService = Depends(get_candidate_service),
) -> CandidateSearchResponse:
    """Execute search_candidates operation."""
    if request.constituency:
        return await service.search_by_constituency(request.constituency)
    if request.lat is not None and request.lng is not None:
        return await service.search_by_location(request.lat, request.lng)
    raise HTTPException(status_code=422, detail="Provide constituency or lat/lng")


@router.get("/{candidate_id}/background", response_model=BackgroundReport)
async def get_background(
    candidate_id: str,
    service: CandidateService = Depends(get_candidate_service),
) -> BackgroundReport:
    """Execute get_background operation."""
    return await service.background_check(candidate_id)


@router.post("/compare", response_model=ComparisonResult)
async def compare_candidates(
    request: CompareRequest,
    service: CandidateService = Depends(get_candidate_service),
) -> ComparisonResult:
    """Execute compare_candidates operation."""
    return await service.compare(request.candidate_ids)
