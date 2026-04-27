from __future__ import annotations



from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_nearby_endpoint_returns_booths() -> None:
    response = client.post(
        "/booth/nearby",
        json={"lat": 28.6139, "lng": 77.209, "radius_km": 5},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["booths"]
    assert body["suggested_visit_time"]["window"] == "10:00-11:30"


def test_nearby_endpoint_validates_input() -> None:
    response = client.post(
        "/booth/nearby",
        json={"lat": 128.6139, "lng": 77.209, "radius_km": 5},
    )

    assert response.status_code == 422


def test_directions_endpoint_returns_route() -> None:
    response = client.post(
        "/booth/directions",
        json={
            "origin": {"lat": 28.6139, "lng": 77.209},
            "destination": {"lat": 28.615, "lng": 77.21},
            "mode": "walking",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["distance"]
    assert body["steps"]


def test_verify_endpoint_returns_nvsp_link() -> None:
    response = client.get("/booth/verify/ABC1234567")

    assert response.status_code == 200
    body = response.json()
    assert body["verified"] is False
    assert "electoralsearch.eci.gov.in" in body["nvsp_url"]
