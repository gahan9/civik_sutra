from __future__ import annotations

from typing import Literal

from pydantic import Field, BaseModel, ConfigDict

TrafficLevel = Literal["low", "moderate", "heavy"]
TravelMode = Literal["walking", "driving", "transit"]
BoothDataSource = Literal["google_maps", "demo_fallback"]


class StrictModel(BaseModel):
    """Model or service class for StrictModel."""

    model_config = ConfigDict(extra="forbid")


class LatLng(StrictModel):
    """Model or service class for LatLng."""

    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class NearbyRequest(StrictModel):
    """Model or service class for NearbyRequest."""

    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=5.0, ge=0.5, le=25.0)


class ManualSearchRequest(StrictModel):
    """Model or service class for ManualSearchRequest."""

    query: str = Field(min_length=3, max_length=160)
    radius_km: float = Field(default=5.0, ge=0.5, le=25.0)


class DirectionsRequest(StrictModel):
    """Model or service class for DirectionsRequest."""

    origin: LatLng
    destination: LatLng
    mode: TravelMode = "walking"


class DirectionStep(StrictModel):
    """Model or service class for DirectionStep."""

    instruction: str
    distance: str


class BoothResult(StrictModel):
    """Model or service class for BoothResult."""

    id: str
    name: str
    address: str
    location: LatLng
    constituency: str
    distance_km: float = Field(ge=0)
    walk_duration_min: int | None = Field(default=None, ge=0)
    drive_duration_min: int | None = Field(default=None, ge=0)
    traffic_level: TrafficLevel
    facilities: list[str] = Field(default_factory=list)
    data_source: BoothDataSource
    is_official_assignment: bool = False
    verification_url: str


class VisitTimeSuggestion(StrictModel):
    """Model or service class for VisitTimeSuggestion."""

    window: str
    reason: str


class NearbyResponse(StrictModel):
    """Model or service class for NearbyResponse."""

    booths: list[BoothResult]
    suggested_visit_time: VisitTimeSuggestion
    source_note: str
    official_verification_url: str


class DirectionsResult(StrictModel):
    """Model or service class for DirectionsResult."""

    distance: str
    duration: str
    duration_in_traffic: str | None
    steps: list[DirectionStep]
    polyline: str
    traffic_level: TrafficLevel


class BoothVerificationResult(StrictModel):
    """Model or service class for BoothVerificationResult."""

    verified: bool
    voter_name: str | None
    assigned_booth: str | None
    constituency: str | None
    nvsp_url: str
    instructions: str
