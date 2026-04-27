import type { CandidateSummary } from "../../types/candidate";

interface CandidateCardProps {
  candidate: CandidateSummary;
  selected: boolean;
  onSelect: (candidate: CandidateSummary) => void;
  onProfile: (candidate: CandidateSummary) => void;
}

function formatInr(amount: number): string {
  if (amount === 0) return "Not declared";
  if (amount >= 10_000_000)
    return `\u20b9${(amount / 10_000_000).toFixed(1)} Cr`;
  if (amount >= 100_000) return `\u20b9${(amount / 100_000).toFixed(1)} L`;
  return `\u20b9${amount.toLocaleString("en-IN")}`;
}

export function CandidateCard({
  candidate,
  selected,
  onSelect,
  onProfile,
}: CandidateCardProps) {
  return (
    <article
      className={`candidate-card${selected ? " candidate-card--selected" : ""}`}
    >
      <div className="candidate-card__header">
        <label className="candidate-card__select">
          <input
            type="checkbox"
            checked={selected}
            onChange={() => onSelect(candidate)}
            aria-label={`Select ${candidate.name} for comparison`}
          />
        </label>
        <div className="candidate-card__identity">
          <h3 className="candidate-card__name">{candidate.name}</h3>
          <span className="candidate-card__party">{candidate.party}</span>
        </div>
      </div>

      <div className="candidate-card__stats">
        <div className="candidate-stat">
          <span className="candidate-stat__icon" aria-hidden="true">
            &#127891;
          </span>
          <span>{candidate.education}</span>
        </div>
        <div className="candidate-stat">
          <span className="candidate-stat__icon" aria-hidden="true">
            &#9878;&#65039;
          </span>
          <span>
            {candidate.criminal_cases === 0
              ? "No criminal cases"
              : `${candidate.criminal_cases} case(s)`}
          </span>
        </div>
        <div className="candidate-stat">
          <span className="candidate-stat__icon" aria-hidden="true">
            &#128176;
          </span>
          <span>{formatInr(candidate.total_assets_inr)}</span>
        </div>
        {candidate.past_positions.length > 0 ? (
          <div className="candidate-stat">
            <span className="candidate-stat__icon" aria-hidden="true">
              &#127963;&#65039;
            </span>
            <span>{candidate.past_positions[0]}</span>
          </div>
        ) : null}
      </div>

      {candidate.age ? (
        <p className="candidate-card__age muted">Age: {candidate.age}</p>
      ) : null}

      <div className="card-actions">
        <button type="button" onClick={() => onProfile(candidate)}>
          Full Profile
        </button>
        <button
          className="secondary"
          type="button"
          onClick={() => onSelect(candidate)}
        >
          {selected ? "Deselect" : "Select"}
        </button>
      </div>
    </article>
  );
}
