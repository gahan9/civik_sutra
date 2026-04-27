from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.models.booth import LatLng, DirectionsRequest
from src.services.geo_service import GeoService


@pytest.fixture
def mock_geo_service() -> GeoService:
    service = GeoService(maps_api_key="fake_api_key")
    return service


@pytest.mark.asyncio
async def test_find_nearby_booths_calls_maps_api(mock_geo_service: GeoService) -> None:
    with patch.object(
        mock_geo_service, "_fetch_json", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = {
            "results": [
                {
                    "place_id": "test_place_1",
                    "name": "Test Polling Station",
                    "formatted_address": "Test Address",
                    "geometry": {"location": {"lat": 28.6, "lng": 77.2}},
                }
            ]
        }

        response = await mock_geo_service.find_nearby_booths(
            lat=28.6139, lng=77.209, radius_km=5.0
        )

        mock_fetch.assert_called_once()
        assert len(response.booths) == 1
        assert response.booths[0].name == "Test Polling Station"
        assert response.booths[0].data_source == "google_maps"


@pytest.mark.asyncio
async def test_get_directions_calls_maps_api(mock_geo_service: GeoService) -> None:
    with patch.object(
        mock_geo_service, "_fetch_json", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = {
            "routes": [
                {
                    "legs": [
                        {
                            "distance": {"text": "2.5 km"},
                            "duration": {"text": "15 mins"},
                            "duration_in_traffic": {"text": "20 mins"},
                            "steps": [
                                {
                                    "html_instructions": "Walk <b>straight</b>",
                                    "distance": {"text": "1 km"},
                                }
                            ],
                        }
                    ],
                    "overview_polyline": {"points": "test_polyline"},
                }
            ]
        }

        request = DirectionsRequest(
            origin=LatLng(lat=28.6, lng=77.2),
            destination=LatLng(lat=28.7, lng=77.3),
            mode="driving",
        )
        response = await mock_geo_service.get_directions(request)

        mock_fetch.assert_called_once()
        assert response is not None
        assert response.distance == "2.5 km"
        assert response.duration == "15 mins"
        assert response.duration_in_traffic == "20 mins"
        assert len(response.steps) == 1
        assert response.steps[0].instruction == "Walk straight"
