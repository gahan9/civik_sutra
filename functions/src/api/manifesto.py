from __future__ import annotations

from fastapi import Depends, APIRouter

from src.models.manifesto import ManifestoComparison, ManifestoCompareRequest
from src.services.manifesto_service import ManifestoService

router = APIRouter(prefix="/manifesto", tags=["manifesto"])


def get_manifesto_service() -> ManifestoService:
    """Execute get_manifesto_service operation."""
    return ManifestoService()


@router.post("/compare", response_model=ManifestoComparison)
async def compare_manifestos(
    request: ManifestoCompareRequest,
    service: ManifestoService = Depends(get_manifesto_service),
) -> ManifestoComparison:
    """Execute compare_manifestos operation."""
    return await service.compare_manifestos(
        party_names=request.party_names,
        categories=request.categories,
        include_past_promises=request.include_past_promises,
    )
