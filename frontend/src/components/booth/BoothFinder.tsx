import { FormEvent, useState } from "react";

import {
  findNearbyBooths,
  getBoothDirections,
  verifyBoothAssignment,
} from "../../lib/api";
import type {
  BoothResult,
  DirectionsResult,
  LatLng,
  NearbyResponse,
} from "../../types/booth";
import { useGeolocation } from "../../hooks/useGeolocation";
import { BoothDetail } from "./BoothDetail";
import { BoothMap } from "./BoothMap";


const DEFAULT_RADIUS_KM = 5;
const DELHI_FALLBACK_LOCATION: LatLng = {
  lat: 28.6139,
  lng: 77.209,
};

export function BoothFinder() {
  const geolocation = useGeolocation();
  const [manualQuery, setManualQuery] = useState("");
  const [nearby, setNearby] = useState<NearbyResponse | null>(null);
  const [selectedBooth, setSelectedBooth] = useState<BoothResult | null>(null);
  const [directions, setDirections] = useState<DirectionsResult | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function searchFromLocation(location: LatLng): Promise<void> {
    setStatus("Finding nearby booths...");
    setError(null);
    const response = await findNearbyBooths({
      ...location,
      radius_km: DEFAULT_RADIUS_KM,
    });
    setNearby(response);
    setSelectedBooth(response.booths[0] ?? null);
    setDirections(null);
    setStatus(null);
  }

  async function handleUseLocation(): Promise<void> {
    geolocation.requestLocation();
    if (geolocation.location) {
      await searchFromLocation(geolocation.location);
    } else {
      await searchFromLocation(DELHI_FALLBACK_LOCATION);
    }
  }

  async function handleManualSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (manualQuery.trim().length < 3) {
      setError("Enter at least 3 characters for pincode or address search.");
      return;
    }
    await searchFromLocation(DELHI_FALLBACK_LOCATION);
    setStatus(`Showing demo booth results for "${manualQuery.trim()}".`);
  }

  async function handleDirections(booth: BoothResult): Promise<void> {
    setSelectedBooth(booth);
    setStatus("Calculating directions...");
    setError(null);
    const result = await getBoothDirections({
      origin: geolocation.location ?? DELHI_FALLBACK_LOCATION,
      destination: booth.location,
      mode: "walking",
    });
    setDirections(result);
    setStatus(null);
  }

  async function handleVerify(booth: BoothResult): Promise<void> {
    setSelectedBooth(booth);
    const result = await verifyBoothAssignment("EPIC");
    window.open(result.nvsp_url, "_blank", "noopener,noreferrer");
  }

  const booths = nearby?.booths ?? [];

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">CivikSutra Booth Finder</p>
        <h1>Find Your Polling Booth</h1>
        <p>
          Use your current location or a manual pincode/address fallback to
          discover nearby polling booths, travel time, traffic level, and the
          best window to visit.
        </p>
        <div className="hero-actions">
          <button type="button" onClick={() => void handleUseLocation()}>
            {geolocation.loading ? "Locating..." : "Use my current location"}
          </button>
        </div>
        {geolocation.error ? <p className="alert">{geolocation.error}</p> : null}
      </section>

      <section className="manual-search" aria-labelledby="manual-search-title">
        <h2 id="manual-search-title">Or enter manually</h2>
        <form onSubmit={(event) => void handleManualSearch(event)}>
          <label htmlFor="manual-query">Pincode or address</label>
          <div className="input-row">
            <input
              id="manual-query"
              name="manual-query"
              value={manualQuery}
              onChange={(event) => setManualQuery(event.target.value)}
              placeholder="e.g. New Delhi 110001"
            />
            <button type="submit">Search</button>
          </div>
        </form>
      </section>

      {error ? <p className="alert">{error}</p> : null}
      {status ? <p className="status">{status}</p> : null}

      <section className="booth-layout">
        <div className="map-panel">
          <BoothMap
            booths={booths}
            selectedBoothId={selectedBooth?.id ?? null}
            userLocation={geolocation.location ?? DELHI_FALLBACK_LOCATION}
            onSelectBooth={setSelectedBooth}
          />
        </div>

        <div className="results-panel">
          <div className="section-heading">
            <h2>Nearby Booths ({booths.length} found)</h2>
            {nearby ? (
              <p>
                Best time to visit:{" "}
                <strong>{nearby.suggested_visit_time.window}</strong>
              </p>
            ) : null}
          </div>
          {booths.length > 0 ? (
            booths.map((booth) => (
              <BoothDetail
                booth={booth}
                key={booth.id}
                onDirections={handleDirections}
                onVerify={handleVerify}
              />
            ))
          ) : (
            <p className="empty-state">
              Start with GPS or manual search to see nearby polling booths.
            </p>
          )}
        </div>
      </section>

      {directions ? (
        <section className="directions-panel" aria-labelledby="directions-title">
          <h2 id="directions-title">Directions</h2>
          <p>
            {directions.distance}, {directions.duration}
          </p>
          <ol>
            {directions.steps.map((step) => (
              <li key={`${step.instruction}-${step.distance}`}>
                {step.instruction} ({step.distance})
              </li>
            ))}
          </ol>
        </section>
      ) : null}
    </main>
  );
}
