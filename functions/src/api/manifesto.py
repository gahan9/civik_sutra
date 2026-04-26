from __future__ import annotations

from fastapi import APIRouter, Depends

from src.models.manifesto import ManifestoCompareRequest, ManifestoComparison
from src.services.manifesto_service import ManifestoService

router = APIRouter(prefix="/manifesto", tags=["manifesto"])


def get_manifesto_service() -> ManifestoService:
    return ManifestoService()


@router.post("/compare", response_model=ManifestoComparison)
async def compare_manifestos(
    request: ManifestoCompareRequest,
    service: ManifestoService = Depends(get_manifesto_service),
) -> ManifestoComparison:
    return await service.compare_manifestos(
        party_names=request.party_names,
        categories=request.categories,
        include_past_promises=request.include_past_promises,
    )
