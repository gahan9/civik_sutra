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
  const [epicNumber, setEpicNumber] = useState("");
  const [nearby, setNearby] = useState<NearbyResponse | null>(null);
  const [selectedBooth, setSelectedBooth] = useState<BoothResult | null>(null);
  const [directions, setDirections] = useState<DirectionsResult | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function searchFromLocation(location: LatLng): Promise<void> {
    try {
      setStatus("Finding nearby booths...");
      setError(null);
      const response = await findNearbyBooths({
        ...location,
        radius_km: DEFAULT_RADIUS_KM,
      });
      setNearby(response);
      setSelectedBooth(response.booths[0] ?? null);
      setDirections(null);
    } catch {
      setError("Unable to fetch booth data right now. Please try again.");
    } finally {
      setStatus(null);
    }
  }

  async function handleUseLocation(): Promise<void> {
    const location = await geolocation.requestLocation();
    await searchFromLocation(location ?? DELHI_FALLBACK_LOCATION);
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
    try {
      setSelectedBooth(booth);
      setStatus("Calculating directions...");
      setError(null);
      const result = await getBoothDirections({
        origin: geolocation.location ?? DELHI_FALLBACK_LOCATION,
        destination: booth.location,
        mode: "walking",
      });
      setDirections(result);
    } catch {
      setError("Unable to calculate directions right now.");
    } finally {
      setStatus(null);
    }
  }

  async function handleVerify(booth: BoothResult): Promise<void> {
    if (epicNumber.trim().length < 6) {
      setError("Enter your EPIC number before opening official verification.");
      return;
    }
    setSelectedBooth(booth);
    const result = await verifyBoothAssignment(epicNumber);
    window.open(result.nvsp_url, "_blank", "noopener,noreferrer");
  }

  const booths = nearby?.booths ?? [];

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">CivikSutra Booth Finder</p>
        <h1>Find Your Polling Booth</h1>
        <p>
          Find nearby polling places, see travel guidance, and verify your
          official assigned booth through the Election Commission before voting.
        </p>
        <div className="impact-grid" aria-label="CivikSutra value highlights">
          <span>GPS booth discovery</span>
          <span>Traffic-aware timing</span>
          <span>ECI verification handoff</span>
          <span>Privacy-first: no voter roll storage</span>
        </div>
        <div className="hero-actions">
          <button type="button" onClick={() => void handleUseLocation()}>
            {geolocation.loading ? "Locating..." : "Use my current location"}
          </button>
        </div>
        {geolocation.error ? (
          <p className="alert">{geolocation.error}</p>
        ) : null}
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

      <section className="trust-panel" aria-labelledby="trust-title">
        <div>
          <p className="eyebrow">Official verification required</p>
          <h2 id="trust-title">Nearest booth is guidance, not assignment</h2>
          <p>
            Indian polling booths are assigned from the electoral roll.
            CivikSutra helps you locate nearby polling places and then hands off
            to ECI for authoritative verification.
          </p>
        </div>
        <label htmlFor="epic-number">EPIC number for ECI lookup</label>
        <div className="input-row">
          <input
            id="epic-number"
            name="epic-number"
            value={epicNumber}
            onChange={(event) =>
              setEpicNumber(event.target.value.toUpperCase())
            }
            placeholder="e.g. ABC1234567"
          />
          <a
            className="button-link secondary"
            href={
              nearby?.official_verification_url ??
              "https://electoralsearch.eci.gov.in/"
            }
            rel="noreferrer"
            target="_blank"
          >
            Open ECI Portal
          </a>
        </div>
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
              <>
                <p>
                  Best time to visit:{" "}
                  <strong>{nearby.suggested_visit_time.window}</strong>
                </p>
                <p className="source-note">{nearby.source_note}</p>
              </>
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
        <section
          className="directions-panel"
          aria-labelledby="directions-title"
        >
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

      <section className="readiness-panel" aria-labelledby="readiness-title">
        <p className="eyebrow">Voting day readiness</p>
        <h2 id="readiness-title">Before you go</h2>
        <ul>
          <li>Carry an accepted ID and check your assigned booth on ECI.</li>
          <li>Plan extra time if traffic is moderate or heavy.</li>
          <li>Use NOTA or ask polling staff if you need procedural help.</li>
        </ul>
      </section>
    </main>
  );
}
