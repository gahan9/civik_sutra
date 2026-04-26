from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TrafficLevel = Literal["low", "moderate", "heavy"]
TravelMode = Literal["walking", "driving", "transit"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LatLng(StrictModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class NearbyRequest(StrictModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=5.0, ge=0.5, le=25.0)


class ManualSearchRequest(StrictModel):
    query: str = Field(min_length=3, max_length=160)
    radius_km: float = Field(default=5.0, ge=0.5, le=25.0)


class DirectionsRequest(StrictModel):
    origin: LatLng
    destination: LatLng
    mode: TravelMode = "walking"


class DirectionStep(StrictModel):
    instruction: str
    distance: str


class BoothResult(StrictModel):
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


class VisitTimeSuggestion(StrictModel):
    window: str
    reason: str


class NearbyResponse(StrictModel):
    booths: list[BoothResult]
    suggested_visit_time: VisitTimeSuggestion


class DirectionsResult(StrictModel):
    distance: str
    duration: str
    duration_in_traffic: str | None
    steps: list[DirectionStep]
    polyline: str
    traffic_level: TrafficLevel


class BoothVerificationResult(StrictModel):
    verified: bool
    voter_name: str | None
    assigned_booth: str | None
    constituency: str | None
    nvsp_url: str
    instructions: str
