# Feature: Booth Finder

**Module**: `booth` | **Phase**: 1 (Foundation) | **Priority**: P0

GPS-based polling booth discovery, map navigation with directions, live traffic analysis, and optimal visit time suggestion.

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|------------|
| BF-1 | Voter | See nearby polling booths on a map based on my GPS location | I know where to go without searching manually |
| BF-2 | Voter | Get walking/driving directions to a selected booth | I can navigate there easily from my phone |
| BF-3 | Voter | See current traffic conditions to the booth | I can plan my travel time accurately |
| BF-4 | Voter | Get a suggested best time to visit | I avoid peak crowds and long queues |
| BF-5 | Voter | Verify my booth assignment using my EPIC number | I confirm I'm going to the correct booth |
| BF-6 | Voter | Enter a pincode or address manually if GPS is denied | I can still find booths without location permission |

## UI Wireframe

```
┌─────────────────────────────────────┐
│  🗺️  Find Your Polling Booth        │
│  ┌─────────────────────────────────┐│
│  │                                 ││
│  │         MAP VIEW                ││
│  │    (Google Maps with markers)   ││
│  │         📍 📍 📍               ││
│  │     📍       📍                ││
│  │  [You are here]                 ││
│  │                                 ││
│  └─────────────────────────────────┘│
│                                     │
│  ── or enter manually ──            │
│  ┌─────────────────────┐ ┌────────┐│
│  │ Pincode / Address   │ │ Search ││
│  └─────────────────────┘ └────────┘│
│                                     │
│  Nearby Booths (3 found)            │
│  ┌─────────────────────────────────┐│
│  │ 📍 Govt. Primary School         ││
│  │    Ward 42, 0.8 km away         ││
│  │    🚶 12 min walk │ 🚗 4 min   ││
│  │    🟢 Low traffic now           ││
│  │    [Directions] [Verify Booth]  ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ 📍 Community Hall               ││
│  │    Sector 5, 1.2 km away        ││
│  │    🚶 18 min walk │ 🚗 6 min   ││
│  │    🟡 Moderate traffic           ││
│  │    [Directions] [Verify Booth]  ││
│  └─────────────────────────────────┘│
│                                     │
│  Best time to visit: 10:00-11:30 AM │
│  (Based on historical traffic)      │
└─────────────────────────────────────┘
```

## Backend API

### `POST /booth/nearby`

Find polling booths near a GPS coordinate.

**Request**:
```json
{
  "lat": 28.6139,
  "lng": 77.2090,
  "radius_km": 5
}
```

**Response**:
```json
{
  "booths": [
    {
      "id": "booth_ward42_gps",
      "name": "Govt. Primary School, Ward 42",
      "address": "Near Hanuman Mandir, Sector 12, New Delhi",
      "location": { "lat": 28.6150, "lng": 77.2100 },
      "constituency": "New Delhi",
      "distance_km": 0.8,
      "walk_duration_min": 12,
      "drive_duration_min": 4,
      "traffic_level": "low",
      "facilities": ["wheelchair_ramp", "drinking_water"]
    }
  ],
  "suggested_visit_time": {
    "window": "10:00-11:30",
    "reason": "Historically lowest traffic; early voters cleared, lunch crowd not arrived"
  }
}
```

### `POST /booth/directions`

Get turn-by-turn directions with traffic.

**Request**:
```json
{
  "origin": { "lat": 28.6139, "lng": 77.2090 },
  "destination": { "lat": 28.6150, "lng": 77.2100 },
  "mode": "walking"
}
```

**Response**:
```json
{
  "distance": "0.8 km",
  "duration": "12 min",
  "duration_in_traffic": "12 min",
  "steps": [
    { "instruction": "Head north on MG Road", "distance": "200 m" },
    { "instruction": "Turn right at Hanuman Mandir", "distance": "600 m" }
  ],
  "polyline": "encoded_polyline_string",
  "traffic_level": "low"
}
```

### `GET /booth/verify/{epic_number}`

Verify voter's assigned booth via EPIC (voter ID) number.

**Response**:
```json
{
  "verified": true,
  "voter_name": "Partial Name***",
  "assigned_booth": "Booth 42 - Govt. Primary School",
  "constituency": "New Delhi",
  "nvsp_url": "https://www.nvsp.in/...",
  "instructions": "Visit NVSP portal to see full details and download e-EPIC"
}
```

## Service Layer

### `GeoService` (`functions/src/services/geo_service.py`)

```python
class GeoService:
    """Handles all location-based operations using Google Maps Platform."""

    async def find_nearby_booths(
        self, lat: float, lng: float, radius_km: float = 5.0
    ) -> list[BoothResult]:
        """Find polling booths near coordinates.

        Strategy:
        1. Check Firestore cache (geohash prefix match)
        2. On miss: Google Maps Places API text search for "polling booth"
        3. For top N results: fetch walking + driving duration
        4. Cache results in Firestore (TTL: 7 days)
        """

    async def get_directions(
        self, origin: LatLng, destination: LatLng, mode: TravelMode = "walking"
    ) -> DirectionsResult:
        """Get directions with traffic-aware duration.

        Uses Google Maps Directions API with departure_time=now
        for real-time traffic data (driving mode only).
        """

    async def get_traffic_estimate(
        self, origin: LatLng, destination: LatLng
    ) -> TrafficEstimate:
        """Compare normal vs traffic duration to classify traffic level.

        Returns: low (< 1.2x), moderate (1.2-1.5x), heavy (> 1.5x)
        """

    def suggest_best_visit_time(self, booth_id: str) -> VisitTimeSuggestion:
        """Suggest optimal voting time based on heuristics.

        Heuristic model (no historical data available for real booths):
        - 7:00-8:00: Moderate (early rush)
        - 8:00-10:00: High (peak morning)
        - 10:00-11:30: Low (sweet spot)
        - 11:30-14:00: Moderate (lunch crowd)
        - 14:00-16:00: Low (afternoon lull)
        - 16:00-18:00: High (evening rush)
        """
```

## Data Models

### Pydantic Models (`functions/src/models/booth.py`)

```python
class LatLng(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)

class NearbyRequest(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=5.0, ge=0.5, le=25.0)

class DirectionsRequest(BaseModel):
    origin: LatLng
    destination: LatLng
    mode: Literal["walking", "driving", "transit"] = "walking"

class BoothResult(BaseModel):
    id: str
    name: str
    address: str
    location: LatLng
    constituency: str
    distance_km: float
    walk_duration_min: int | None
    drive_duration_min: int | None
    traffic_level: Literal["low", "moderate", "heavy"]
    facilities: list[str]

class DirectionsResult(BaseModel):
    distance: str
    duration: str
    duration_in_traffic: str | None
    steps: list[DirectionStep]
    polyline: str
    traffic_level: Literal["low", "moderate", "heavy"]

class VisitTimeSuggestion(BaseModel):
    window: str
    reason: str
```

## Frontend Components

### `BoothMap` (`frontend/src/components/booth/BoothMap.tsx`)

Google Maps component with:
- User location marker (blue dot)
- Booth markers (red pins) with info windows
- Route polyline overlay when directions active
- Traffic layer toggle

**Dependencies**: `@react-google-maps/api`

### `BoothDetail` (`frontend/src/components/booth/BoothDetail.tsx`)

Card component showing:
- Booth name and address
- Walking and driving duration
- Traffic indicator (color-coded badge)
- "Get Directions" button (opens route on map)
- "Verify Booth" button (opens EPIC verification)

### `useGeolocation` (`frontend/src/hooks/useGeolocation.ts`)

Custom hook:
- Requests `navigator.geolocation` permission
- Returns `{ lat, lng, loading, error, denied }`
- Falls back to manual input UI when denied

## Unit Tests

### Backend Tests (`functions/tests/test_geo_service.py`)

```python
class TestGeoService:
    """Unit tests for GeoService with mocked Google Maps API."""

    async def test_find_nearby_returns_sorted_by_distance(self):
        """Booths should be sorted nearest-first."""

    async def test_find_nearby_uses_cache_on_hit(self):
        """Cached results should be returned without calling Maps API."""

    async def test_find_nearby_calls_api_on_cache_miss(self):
        """Cache miss should trigger Google Maps Places API call."""

    async def test_find_nearby_validates_radius_bounds(self):
        """Radius outside 0.5-25 km should raise validation error."""

    async def test_directions_walking_mode(self):
        """Walking directions should not include traffic data."""

    async def test_directions_driving_with_traffic(self):
        """Driving directions should include duration_in_traffic."""

    async def test_traffic_estimate_low(self):
        """Traffic ratio < 1.2 should classify as 'low'."""

    async def test_traffic_estimate_moderate(self):
        """Traffic ratio 1.2-1.5 should classify as 'moderate'."""

    async def test_traffic_estimate_heavy(self):
        """Traffic ratio > 1.5 should classify as 'heavy'."""

    def test_suggest_visit_time_morning_sweet_spot(self):
        """10:00-11:30 should be suggested during morning hours."""

    def test_suggest_visit_time_afternoon_lull(self):
        """14:00-16:00 should be suggested during afternoon hours."""
```

### API Tests (`functions/tests/test_booth_api.py`)

```python
class TestBoothAPI:
    """Integration tests for booth HTTP endpoints."""

    async def test_nearby_endpoint_returns_200(self):
        """Valid lat/lng should return booth list."""

    async def test_nearby_endpoint_validates_input(self):
        """Invalid coordinates should return 422."""

    async def test_directions_endpoint_returns_route(self):
        """Valid origin/destination should return directions."""

    async def test_verify_endpoint_returns_nvsp_link(self):
        """EPIC number should return verification URL."""

    async def test_nearby_endpoint_rate_limited(self):
        """Exceeding daily quota should return 429."""
```

## Google Maps API Usage

| API | Calls Per User Session | Daily Budget |
|-----|----------------------|--------------|
| Places API (text search) | 1 (cached after) | ~50 |
| Directions API | 1-3 per booth selected | ~200 |
| Maps JavaScript (client) | Unlimited (map loads) | N/A (client-side) |

**Cost control**: Cache aggressively in Firestore. A booth's location doesn't change -- cache for 7 days.

## Edge Cases

| Scenario | Handling |
|----------|----------|
| GPS denied | Show manual input (pincode/address) with geocoding |
| No booths within radius | Expand radius to 10km, then 25km, then show message |
| Google Maps API down | Return Firestore-cached booths (possibly stale) |
| User outside India | Show message: "This service covers Indian elections only" |
| Multiple booths same location | De-duplicate by address before displaying |
