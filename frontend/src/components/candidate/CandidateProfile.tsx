import { useEffect, useState } from "react";

import { getCandidateBackground } from "../../lib/candidate-api";
import type { BackgroundReport, CandidateSummary } from "../../types/candidate";


interface CandidateProfileProps {
  candidate: CandidateSummary;
  onBack: () => void;
}

function formatInr(amount: number): string {
  if (amount === 0) return "Not declared";
  if (amount >= 10_000_000) return `\u20b9${(amount / 10_000_000).toFixed(1)} Crore`;
  if (amount >= 100_000) return `\u20b9${(amount / 100_000).toFixed(1)} Lakh`;
  return `\u20b9${amount.toLocaleString("en-IN")}`;
}

const sentimentClass: Record<string, string> = {
  positive: "sentiment--positive",
  negative: "sentiment--negative",
  neutral: "sentiment--neutral",
};

export function CandidateProfile({ candidate, onBack }: CandidateProfileProps) {
  const [report, setReport] = useState<BackgroundReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const result = await getCandidateBackground(candidate.id);
        if (!cancelled) setReport(result);
      } catch {
        if (!cancelled) setError("Unable to load background report.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => { cancelled = true; };
  }, [candidate.id]);

  return (
    <section className="profile-panel" aria-labelledby="profile-title">
      <button className="secondary profile-back" type="button" onClick={onBack}>
        &larr; Back to results
      </button>

      <div className="profile-header">
        <h2 id="profile-title">{candidate.name}</h2>
        <span className="candidate-card__party">{candidate.party}</span>
      </div>

      <dl className="profile-grid">
        <div>
          <dt>Education</dt>
          <dd>{candidate.education}</dd>
        </div>
        {candidate.age ? (
          <div>
            <dt>Age</dt>
            <dd>{candidate.age}</dd>
          </div>
        ) : null}
        <div>
          <dt>Criminal Cases</dt>
          <dd>
            {candidate.criminal_cases === 0
              ? "No criminal cases declared"
              : `${candidate.criminal_cases} case(s)`}
          </dd>
        </div>
        <div>
          <dt>Total Assets</dt>
          <dd>{formatInr(candidate.total_assets_inr)}</dd>
        </div>
        <div>
          <dt>Liabilities</dt>
          <dd>{formatInr(candidate.total_liabilities_inr)}</dd>
        </div>
        {candidate.past_positions.length > 0 ? (
          <div>
            <dt>Past Positions</dt>
            <dd>{candidate.past_positions.join(", ")}</dd>
          </div>
        ) : null}
      </dl>

      {loading ? <p className="status">Loading background report...</p> : null}
      {error ? <p className="alert">{error}</p> : null}

      {report ? (
        <>
          <div className="profile-section">
            <h3>Asset Breakdown</h3>
            <dl className="profile-grid">
              <div>
                <dt>Movable</dt>
                <dd>{formatInr(report.asset_breakdown.movable)}</dd>
              </div>
              <div>
                <dt>Immovable</dt>
                <dd>{formatInr(report.asset_breakdown.immovable)}</dd>
              </div>
              {report.asset_breakdown.vehicles.length > 0 ? (
                <div>
                  <dt>Vehicles</dt>
                  <dd>{report.asset_breakdown.vehicles.join(", ")}</dd>
                </div>
              ) : null}
            </dl>
          </div>

          {report.grounding.recent_news.length > 0 ? (
            <div className="profile-section">
              <h3>Recent News</h3>
              <ul className="news-list">
                {report.grounding.recent_news.map((item) => (
                  <li key={item.title} className="news-item">
                    <span className={`sentiment-dot ${sentimentClass[item.sentiment]}`} />
                    <div>
                      <p className="news-title">
                        {item.url ? (
                          <a href={item.url} target="_blank" rel="noreferrer">
                            {item.title}
                          </a>
                        ) : (
                          item.title
                        )}
                      </p>
                      <p className="muted">
                        {item.source} &middot; {item.date}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {report.grounding.achievements.length > 0 ? (
            <div className="profile-section">
              <h3>Achievements</h3>
              <ul>
                {report.grounding.achievements.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {report.grounding.controversies.length > 0 ? (
            <div className="profile-section">
              <h3>Controversies</h3>
              <ul>
                {report.grounding.controversies.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {report.grounding.social_media_presence ? (
            <div className="profile-section">
              <h3>Social Media</h3>
              <p>{report.grounding.social_media_presence}</p>
            </div>
          ) : null}

          {Object.keys(report.source_urls).length > 0 ? (
            <div className="profile-section">
              <h3>Data Sources</h3>
              <ul>
                {Object.entries(report.source_urls).map(([label, url]) => (
                  <li key={label}>
                    <a href={url} target="_blank" rel="noreferrer">
                      {label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
