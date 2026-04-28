import type { BoothResult } from "../../types/booth";

interface BoothDetailProps {
  booth: BoothResult;
  onDirections: (booth: BoothResult) => void;
  onVerify: (booth: BoothResult) => void;
}

const trafficLabels: Record<BoothResult["traffic_level"], string> = {
  low: "Low traffic now",
  moderate: "Moderate traffic now",
  heavy: "Heavy traffic now",
};

const sourceLabels: Record<BoothResult["data_source"], string> = {
  google_maps: "Maps result",
  demo_fallback: "Demo fallback",
};

export function BoothDetail({ booth, onDirections, onVerify }: BoothDetailProps) {
  return (
    <article className="booth-card">
      <div>
        <div className="badge-row">
          <p className={`traffic-badge ${booth.traffic_level}`}>
            {trafficLabels[booth.traffic_level]}
          </p>
          <p className="source-badge">{sourceLabels[booth.data_source]}</p>
        </div>
        <h3>{booth.name}</h3>
        <p>{booth.address}</p>
        <p className="muted">
          {booth.constituency} constituency, {booth.distance_km.toFixed(1)} km away
        </p>
        {!booth.is_official_assignment ? (
          <p className="verification-note">
            Nearby place only. Verify your assigned booth with ECI before voting.
          </p>
        ) : null}
      </div>

      <dl className="duration-grid">
        <div>
          <dt>Walk</dt>
          <dd>{booth.walk_duration_min ?? "N/A"} min</dd>
        </div>
        <div>
          <dt>Drive</dt>
          <dd>{booth.drive_duration_min ?? "N/A"} min</dd>
        </div>
      </dl>

      <div className="facility-list" aria-label="Facilities">
        {booth.facilities.map((facility) => (
          <span key={facility}>{facility.replaceAll("_", " ")}</span>
        ))}
      </div>

      <div className="card-actions">
        <button type="button" onClick={() => onDirections(booth)}>
          Directions
        </button>
        <button className="secondary" type="button" onClick={() => onVerify(booth)}>
          Verify Booth
        </button>
      </div>
    </article>
  );
}
