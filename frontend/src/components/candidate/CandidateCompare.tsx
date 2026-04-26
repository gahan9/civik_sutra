import { useEffect, useState } from "react";

import { compareCandidates } from "../../lib/candidate-api";
import type { CandidateSummary, ComparisonResult } from "../../types/candidate";


interface CandidateCompareProps {
  candidates: CandidateSummary[];
  onBack: () => void;
}

const dimensionLabels: Record<string, string> = {
  education: "Education",
  age: "Age",
  criminal_cases: "Criminal Cases",
  total_assets: "Total Assets",
  total_liabilities: "Liabilities",
  past_work: "Past Work",
  key_promises: "Key Promises",
  recent_news: "Recent News (30 days)",
  delivery_probability: "Delivery Probability",
};

export function CandidateCompare({ candidates, onBack }: CandidateCompareProps) {
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const comparison = await compareCandidates({
          candidate_ids: candidates.map((c) => c.id),
        });
        if (!cancelled) setResult(comparison);
      } catch {
        if (!cancelled) setError("Unable to generate comparison.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => { cancelled = true; };
  }, [candidates]);

  return (
    <section className="compare-panel" aria-labelledby="compare-title">
      <button className="secondary profile-back" type="button" onClick={onBack}>
        &larr; Back to results
      </button>

      <p className="eyebrow">Candidate Comparison</p>
      <h2 id="compare-title">
        Side-by-Side Analysis ({candidates.length} candidates)
      </h2>

      {loading ? <p className="status">Generating comparison...</p> : null}
      {error ? <p className="alert">{error}</p> : null}

      {result ? (
        <>
          <div className="compare-table-wrapper">
            <table className="compare-table" role="grid">
              <thead>
                <tr>
                  <th scope="col">Dimension</th>
                  {candidates.map((c) => (
                    <th key={c.id} scope="col">
                      <span className="compare-name">{c.name}</span>
                      <span className="compare-party">{c.party}</span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.dimensions.map((dim) => (
                  <tr key={dim}>
                    <td className="compare-dim-label">
                      {dimensionLabels[dim] ?? dim}
                    </td>
                    {candidates.map((c) => (
                      <td key={c.id}>
                        {result.candidates[c.id]?.[dim] ?? "N/A"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="compare-analysis">
            <h3>AI Analysis</h3>
            <p>{result.ai_analysis}</p>
            {result.ai_analysis_citations.length > 0 ? (
              <p className="muted">
                Sources:{" "}
                {result.ai_analysis_citations.map((c, i) => (
                  <span key={c.source}>
                    {i > 0 ? ", " : ""}
                    {c.url ? (
                      <a href={c.url} target="_blank" rel="noreferrer">
                        {c.source}
                      </a>
                    ) : (
                      c.source
                    )}
                  </span>
                ))}
              </p>
            ) : null}
          </div>
        </>
      ) : null}
    </section>
  );
}
