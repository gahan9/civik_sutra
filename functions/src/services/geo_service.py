from __future__ import annotations

import asyncio
import json
import os
import re
import urllib.parse
import urllib.request
from math import asin, cos, radians, sin, sqrt
from typing import Any

from src.models.booth import (
    BoothResult,
    BoothVerificationResult,
    DirectionStep,
    DirectionsRequest,
    DirectionsResult,
    LatLng,
    NearbyRequest,
    NearbyResponse,
    TrafficLevel,
    VisitTimeSuggestion,
)


PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
MAX_LIVE_BOOTHS = 3


class GeoService:
    """Location service for polling booth discovery and route guidance."""

    def __init__(self, maps_api_key: str | None = None) -> None:
        self._maps_api_key = maps_api_key or os.getenv("EP_GOOGLE_MAPS_API_KEY")

    async def find_nearby_booths(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
    ) -> NearbyResponse:
        request = NearbyRequest(lat=lat, lng=lng, radius_km=radius_km)
        origin = LatLng(lat=request.lat, lng=request.lng)

        if self._maps_api_key:
            live_booths = await self._find_live_booths(request, origin)
            if live_booths:
                return NearbyResponse(
                    booths=live_booths,
                    suggested_visit_time=self.suggest_best_visit_time(
                        live_booths[0].id
                    ),
                )

        booths = [
            self._with_distance(origin, booth)
            for booth in self._demo_booths()
            if self._distance_km(origin, booth.location) <= request.radius_km
        ]
        booths.sort(key=lambda booth: booth.distance_km)

        return NearbyResponse(
            booths=booths,
            suggested_visit_time=self.suggest_best_visit_time(
                booths[0].id if booths else "default"
            ),
        )

    async def get_directions(self, request: DirectionsRequest) -> DirectionsResult:
        if self._maps_api_key:
            live_directions = await self._get_live_directions(request)
            if live_directions:
                return live_directions

        distance_km = self._distance_km(request.origin, request.destination)
        walk_minutes = max(1, round(distance_km / 4.5 * 60))
        drive_minutes = max(1, round(distance_km / 18 * 60))

        if request.mode == "driving":
            traffic_minutes = max(drive_minutes + 1, round(drive_minutes * 1.2))
            traffic_level = self.classify_traffic_level(drive_minutes, traffic_minutes)
            duration = f"{drive_minutes} min"
            duration_in_traffic = f"{traffic_minutes} min"
        elif request.mode == "transit":
            traffic_level = "low"
            duration = f"{max(walk_minutes, drive_minutes + 8)} min"
            duration_in_traffic = None
        else:
            traffic_level = "low"
            duration = f"{walk_minutes} min"
            duration_in_traffic = None

        return DirectionsResult(
            distance=f"{distance_km:.1f} km",
            duration=duration,
            duration_in_traffic=duration_in_traffic,
            steps=[
                DirectionStep(
                    instruction="Start from your current location",
                    distance="100 m",
                ),
                DirectionStep(
                    instruction="Continue towards the selected polling booth",
                    distance=f"{max(distance_km - 0.1, 0):.1f} km",
                ),
            ],
            polyline="",
            traffic_level=traffic_level,
        )

    async def verify_booth_assignment(self, epic_number: str) -> BoothVerificationResult:
        encoded_epic = epic_number.strip().upper()
        return BoothVerificationResult(
            verified=False,
            voter_name=None,
            assigned_booth=None,
            constituency=None,
            nvsp_url=f"https://electoralsearch.eci.gov.in/?epic={encoded_epic}",
            instructions=(
                "Use the Election Commission voter search portal to verify your "
                "assigned booth. CivikSutra does not store or display private "
                "voter-roll details."
            ),
        )

    def suggest_best_visit_time(self, booth_id: str) -> VisitTimeSuggestion:
        return VisitTimeSuggestion(
            window="10:00-11:30",
            reason=(
                "Historically lowest traffic; early voters cleared, lunch crowd "
                "not arrived."
            ),
        )

    @staticmethod
    def classify_traffic_level(
        normal_minutes: int,
        traffic_minutes: int,
    ) -> TrafficLevel:
        ratio = traffic_minutes / max(normal_minutes, 1)
        if ratio < 1.2:
            return "low"
        if ratio <= 1.5:
            return "moderate"
        return "heavy"

    @staticmethod
    def _distance_km(origin: LatLng, destination: LatLng) -> float:
        earth_radius_km = 6371.0
        lat_delta = radians(destination.lat - origin.lat)
        lng_delta = radians(destination.lng - origin.lng)
        origin_lat = radians(origin.lat)
        destination_lat = radians(destination.lat)

        haversine = (
            sin(lat_delta / 2) ** 2
            + cos(origin_lat) * cos(destination_lat) * sin(lng_delta / 2) ** 2
        )
        return 2 * earth_radius_km * asin(sqrt(haversine))

    def _with_distance(self, origin: LatLng, booth: BoothResult) -> BoothResult:
        distance_km = round(self._distance_km(origin, booth.location), 1)
        return booth.model_copy(update={"distance_km": distance_km})

    async def _find_live_booths(
        self,
        request: NearbyRequest,
        origin: LatLng,
    ) -> list[BoothResult]:
        payload = await self._fetch_json(
            PLACES_TEXT_SEARCH_URL,
            {
                "query": "polling station OR polling booth",
                "location": f"{request.lat},{request.lng}",
                "radius": str(round(request.radius_km * 1000)),
                "key": self._maps_api_key or "",
            },
        )
        results = payload.get("results", [])
        if not isinstance(results, list):
            return []

        booths: list[BoothResult] = []
        for index, result in enumerate(results[:MAX_LIVE_BOOTHS]):
            booth = self._booth_from_place(index, result, origin)
            if booth:
                booths.append(booth)
        booths.sort(key=lambda booth: booth.distance_km)
        return booths

    async def _get_live_directions(
        self,
        request: DirectionsRequest,
    ) -> DirectionsResult | None:
        params = {
            "origin": f"{request.origin.lat},{request.origin.lng}",
            "destination": f"{request.destination.lat},{request.destination.lng}",
            "mode": request.mode,
            "key": self._maps_api_key or "",
        }
        if request.mode == "driving":
            params["departure_time"] = "now"

        payload = await self._fetch_json(DIRECTIONS_URL, params)
        routes = payload.get("routes", [])
        if not routes:
            return None

        legs = routes[0].get("legs", [])
        if not legs:
            return None

        leg = legs[0]
        duration_text = leg.get("duration", {}).get("text", "Unknown")
        traffic_text = leg.get("duration_in_traffic", {}).get("text")
        normal_minutes = self._parse_minutes(duration_text)
        traffic_minutes = self._parse_minutes(traffic_text or duration_text)

        return DirectionsResult(
            distance=leg.get("distance", {}).get("text", "Unknown"),
            duration=duration_text,
            duration_in_traffic=traffic_text if request.mode == "driving" else None,
            steps=[
                DirectionStep(
                    instruction=self._strip_html(step.get("html_instructions", "")),
                    distance=step.get("distance", {}).get("text", ""),
                )
                for step in leg.get("steps", [])
            ],
            polyline=routes[0].get("overview_polyline", {}).get("points", ""),
            traffic_level=self.classify_traffic_level(
                normal_minutes,
                traffic_minutes,
            ),
        )

    def _booth_from_place(
        self,
        index: int,
        place: dict[str, Any],
        origin: LatLng,
    ) -> BoothResult | None:
        geometry = place.get("geometry", {}).get("location", {})
        lat = geometry.get("lat")
        lng = geometry.get("lng")
        if not isinstance(lat, int | float) or not isinstance(lng, int | float):
            return None

        location = LatLng(lat=float(lat), lng=float(lng))
        distance_km = round(self._distance_km(origin, location), 1)
        drive_minutes = max(1, round(distance_km / 18 * 60))
        walk_minutes = max(1, round(distance_km / 4.5 * 60))

        return BoothResult(
            id=f"google_place_{place.get('place_id', index)}",
            name=str(place.get("name", "Polling Booth")),
            address=str(place.get("formatted_address", "Address unavailable")),
            location=location,
            constituency="Verify with ECI",
            distance_km=distance_km,
            walk_duration_min=walk_minutes,
            drive_duration_min=drive_minutes,
            traffic_level="low",
            facilities=[],
        )

    async def _fetch_json(
        self,
        url: str,
        params: dict[str, str],
    ) -> dict[str, Any]:
        query = urllib.parse.urlencode(params)
        target_url = f"{url}?{query}"

        def read_url() -> dict[str, Any]:
            request = urllib.request.Request(target_url)
            with urllib.request.urlopen(request, timeout=8) as response:
                body = response.read().decode("utf-8")
            data = json.loads(body)
            return data if isinstance(data, dict) else {}

        try:
            return await asyncio.to_thread(read_url)
        except (OSError, TimeoutError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _strip_html(value: str) -> str:
        return re.sub(r"<[^>]+>", "", value)

    @staticmethod
    def _parse_minutes(value: str) -> int:
        hours_match = re.search(r"(\d+)\s*hour", value)
        minutes_match = re.search(r"(\d+)\s*min", value)
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        return max(1, hours * 60 + minutes)

    @staticmethod
    def _demo_booths() -> list[BoothResult]:
        return [
            BoothResult(
                id="booth_ward42_gps",
                name="Govt. Primary School, Ward 42",
                address="Near Hanuman Mandir, Sector 12, New Delhi",
                location=LatLng(lat=28.6150, lng=77.2100),
                constituency="New Delhi",
                distance_km=0,
                walk_duration_min=12,
                drive_duration_min=4,
                traffic_level="low",
                facilities=["wheelchair_ramp", "drinking_water"],
            ),
            BoothResult(
                id="booth_community_hall_sector5",
                name="Community Hall, Sector 5",
                address="Sector 5 Community Centre, New Delhi",
                location=LatLng(lat=28.6205, lng=77.2164),
                constituency="New Delhi",
                distance_km=0,
                walk_duration_min=18,
                drive_duration_min=6,
                traffic_level="moderate",
                facilities=["drinking_water", "shade"],
            ),
            BoothResult(
                id="booth_model_school_central",
                name="Model School Central",
                address="Central Avenue, New Delhi",
                location=LatLng(lat=28.6079, lng=77.2023),
                constituency="New Delhi",
                distance_km=0,
                walk_duration_min=20,
                drive_duration_min=7,
                traffic_level="low",
                facilities=["wheelchair_ramp", "first_aid"],
            ),
        ]
