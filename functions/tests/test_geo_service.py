from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.booth import LatLng, NearbyRequest, DirectionsRequest
from src.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_find_nearby_returns_sorted_by_distance() -> None:
    service = GeoService()

    response = await service.find_nearby_booths(
        lat=28.6139,
        lng=77.209,
        radius_km=5,
    )

    distances = [booth.distance_km for booth in response.booths]
    assert distances == sorted(distances)
    assert response.suggested_visit_time.window == "10:00-11:30"
    assert "official assigned booth" in response.source_note
    assert response.official_verification_url.startswith("https://electoralsearch")
    assert all(not booth.is_official_assignment for booth in response.booths)


def test_nearby_request_validates_radius_bounds() -> None:
    with pytest.raises(ValidationError):
        NearbyRequest(lat=28.6139, lng=77.209, radius_km=0.1)


def test_nearby_request_validates_coordinate_bounds() -> None:
    with pytest.raises(ValidationError):
        NearbyRequest(lat=128.6139, lng=77.209, radius_km=5)


@pytest.mark.asyncio
async def test_directions_walking_mode_has_no_traffic_duration() -> None:
    service = GeoService()

    directions = await service.get_directions(
        DirectionsRequest(
            origin=LatLng(lat=28.6139, lng=77.209),
            destination=LatLng(lat=28.615, lng=77.21),
            mode="walking",
        )
    )

    assert directions.duration_in_traffic is None
    assert directions.traffic_level == "low"
    assert directions.steps


@pytest.mark.asyncio
async def test_directions_driving_mode_includes_traffic_duration() -> None:
    service = GeoService()

    directions = await service.get_directions(
        DirectionsRequest(
            origin=LatLng(lat=28.6139, lng=77.209),
            destination=LatLng(lat=28.615, lng=77.21),
            mode="driving",
        )
    )

    assert directions.duration_in_traffic is not None
    assert directions.traffic_level in {"low", "moderate", "heavy"}


@pytest.mark.parametrize(
    ("normal_minutes", "traffic_minutes", "expected"),
    [
        (10, 11, "low"),
        (10, 13, "moderate"),
        (10, 16, "heavy"),
    ],
)
def test_classify_traffic_level(
    normal_minutes: int,
    traffic_minutes: int,
    expected: str,
) -> None:
    assert GeoService.classify_traffic_level(normal_minutes, traffic_minutes) == expected


def test_suggest_visit_time_uses_morning_sweet_spot() -> None:
    suggestion = GeoService().suggest_best_visit_time("booth_ward42_gps")

    assert suggestion.window == "10:00-11:30"
    assert "lowest traffic" in suggestion.reason.lower()
