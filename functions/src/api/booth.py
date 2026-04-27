from __future__ import annotations


from fastapi import APIRouter, Depends

from src.models.booth import (
    BoothVerificationResult,
    DirectionsRequest,
    DirectionsResult,
    NearbyRequest,
    NearbyResponse,
)
from src.services.geo_service import GeoService

router = APIRouter(prefix="/booth", tags=["booth"])


def get_geo_service() -> GeoService:
    """Execute get_geo_service operation."""
    return GeoService()


@router.post("/nearby", response_model=NearbyResponse)
async def find_nearby_booths(
    request: NearbyRequest,
    service: GeoService = Depends(get_geo_service),
) -> NearbyResponse:
    """Execute find_nearby_booths operation."""
    return await service.find_nearby_booths(
        lat=request.lat,
        lng=request.lng,
        radius_km=request.radius_km,
    )


@router.post("/directions", response_model=DirectionsResult)
async def get_directions(
    request: DirectionsRequest,
    service: GeoService = Depends(get_geo_service),
) -> DirectionsResult:
    """Execute get_directions operation."""
    return await service.get_directions(request)


@router.get("/verify/{epic_number}", response_model=BoothVerificationResult)
async def verify_booth(
    epic_number: str,
    service: GeoService = Depends(get_geo_service),
) -> BoothVerificationResult:
    """Execute verify_booth operation."""
    return await service.verify_booth_assignment(epic_number)
