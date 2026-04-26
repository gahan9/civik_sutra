export type TrafficLevel = "low" | "moderate" | "heavy";
export type TravelMode = "walking" | "driving" | "transit";
export type BoothDataSource = "google_maps" | "demo_fallback";

export interface LatLng {
  lat: number;
  lng: number;
}

export interface NearbyRequest extends LatLng {
  radius_km: number;
}

export interface DirectionStep {
  instruction: string;
  distance: string;
}

export interface BoothResult {
  id: string;
  name: string;
  address: string;
  location: LatLng;
  constituency: string;
  distance_km: number;
  walk_duration_min: number | null;
  drive_duration_min: number | null;
  traffic_level: TrafficLevel;
  facilities: string[];
  data_source: BoothDataSource;
  is_official_assignment: boolean;
  verification_url: string;
}

export interface VisitTimeSuggestion {
  window: string;
  reason: string;
}

export interface NearbyResponse {
  booths: BoothResult[];
  suggested_visit_time: VisitTimeSuggestion;
  source_note: string;
  official_verification_url: string;
}

export interface DirectionsRequest {
  origin: LatLng;
  destination: LatLng;
  mode: TravelMode;
}

export interface DirectionsResult {
  distance: string;
  duration: string;
  duration_in_traffic: string | null;
  steps: DirectionStep[];
  polyline: string;
  traffic_level: TrafficLevel;
}

export interface BoothVerificationResult {
  verified: boolean;
  voter_name: string | null;
  assigned_booth: string | null;
  constituency: string | null;
  nvsp_url: string;
  instructions: string;
}
