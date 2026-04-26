import { useCallback, useState } from "react";

import { compareManifestos } from "../../lib/manifesto-api";
import type {
  ManifestoComparison as ManifestoComparisonData,
  PromiseTracker,
} from "../../types/manifesto";


const AVAILABLE_PARTIES = ["BJP", "INC", "AAP", "BSP", "TMC", "DMK"];

const CATEGORY_LABELS: Record<string, string> = {
  economy: "Economy & Employment",
  education: "Education",
  healthcare: "Healthcare",
  infrastructure: "Infrastructure",
  defense: "Defense & Security",
  social_welfare: "Social Welfare",
  environment: "Environment & Climate",
  governance: "Governance",
};

const STATUS_LABELS: Record<string, { label: string; className: string }> = {
  fulfilled: { label: "Fulfilled", className: "promise-fulfilled" },
  partial: { label: "Partial", className: "promise-partial" },
  not_met: { label: "Not Met", className: "promise-not-met" },
  ongoing: { label: "Ongoing", className: "promise-ongoing" },
};

export function ManifestoComparison() {
  const [selectedParties, setSelectedParties] = useState<string[]>(["BJP", "INC"]);
  const [comparison, setComparison] = useState<ManifestoComparisonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleParty = useCallback((party: string) => {
    setSelectedParties((prev) => {
      if (prev.includes(party)) {
        return prev.length > 2 ? prev.filter((p) => p !== party) : prev;
      }
      return prev.length < 4 ? [...prev, party] : prev;
    });
  }, []);

  const handleCompare = useCallback(async () => {
    if (selectedParties.length < 2) return;

    setLoading(true);
    setError(null);
    try {
      const result = await compareManifestos({
        party_names: selectedParties,
        include_past_promises: true,
      });
      setComparison(result);
    } catch {
      setError("Failed to load manifesto comparison. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [selectedParties]);

  const handleShare = useCallback(() => {
    if (!comparison) return;
    const text =
      `CivikSutra Manifesto Comparison: ${comparison.parties.join(" vs ")}\n\n` +
      `${comparison.ai_analysis}\n\n` +
      `Compare manifestos at: ${window.location.href}`;
    if (navigator.share) {
      navigator.share({ title: "Manifesto Comparison", text }).catch(() => {});
    } else {
      navigator.clipboard.writeText(text).catch(() => {});
    }
  }, [comparison]);

  return (
    <div className="shell">
      <section className="hero">
        <p className="eyebrow">Manifesto Comparison</p>
        <h1>Compare Party Manifestos</h1>
        <p>
          Side-by-side analysis of party promises across key policy areas.
          Select 2-4 parties to compare their election commitments.
        </p>
      </section>

      <section className="manifesto-selector">
        <label>Select parties to compare (2-4):</label>
        <div className="party-chips">
          {AVAILABLE_PARTIES.map((party) => (
            <button
              key={party}
              type="button"
              className={
                selectedParties.includes(party)
                  ? "party-chip party-chip--active"
                  : "party-chip"
              }
              onClick={() => toggleParty(party)}
            >
              {selectedParties.includes(party) ? "✓ " : ""}
              {party}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={handleCompare}
          disabled={selectedParties.length < 2 || loading}
        >
          {loading ? "Comparing..." : "Compare Manifestos"}
        </button>
      </section>

      {error && <div className="alert">{error}</div>}

      {loading && (
        <div className="status">
          Analyzing manifestos with AI... This may take a moment.
        </div>
      )}

      {comparison && !loading && (
        <>
          <section className="compare-panel">
            <h2>{comparison.parties.join(" vs ")} — Manifesto Comparison</h2>

            <div className="compare-table-wrapper">
              <table className="compare-table">
                <thead>
                  <tr>
                    <th>Category</th>
                    {comparison.parties.map((party) => (
                      <th key={party}>
                        <span className="compare-name">{party}</span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(comparison.categories).map(([cat, partyData]) => (
                    <tr key={cat}>
                      <td className="compare-dim-label">
                        {CATEGORY_LABELS[cat] ?? cat}
                      </td>
                      {comparison.parties.map((party) => (
                        <td key={party}>
                          <ul className="manifesto-promises">
                            {(partyData[party] ?? ["Not addressed"]).map(
                              (promise, idx) => (
                                <li key={idx}>{promise}</li>
                              ),
                            )}
                          </ul>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="compare-analysis">
              <h3>AI Analysis</h3>
              <p>{comparison.ai_analysis}</p>
            </div>
          </section>

          {comparison.past_promises && (
            <section className="compare-panel" style={{ marginTop: "1rem" }}>
              <h2>Past Promise Delivery</h2>
              {Object.entries(comparison.past_promises).map(
                ([party, promises]) => (
                  <div key={party} className="promise-section">
                    <h3>{party} — 2019 Manifesto Promises</h3>
                    <PromiseTable promises={promises} />
                  </div>
                ),
              )}
            </section>
          )}

          <div className="card-actions" style={{ marginTop: "1rem" }}>
            <button type="button" className="secondary" onClick={handleShare}>
              Share Comparison
            </button>
          </div>

          {comparison.sources.length > 0 && (
            <div className="source-note" style={{ marginTop: "1rem" }}>
              <strong>Sources: </strong>
              {comparison.sources.map((s, i) => (
                <span key={i}>
                  {s.manifesto_url ? (
                    <a
                      href={s.manifesto_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {s.party}
                    </a>
                  ) : (
                    s.party
                  )}
                  {i < comparison.sources.length - 1 ? " · " : ""}
                </span>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}


function PromiseTable({ promises }: { promises: PromiseTracker[] }) {
  if (promises.length === 0) {
    return <p className="muted">No tracked promises for this party.</p>;
  }

  return (
    <div className="compare-table-wrapper">
      <table className="compare-table">
        <thead>
          <tr>
            <th>Promise</th>
            <th>Status</th>
            <th>Evidence</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
          {promises.map((p, idx) => {
            const statusInfo = STATUS_LABELS[p.status] ?? {
              label: p.status,
              className: "",
            };
            return (
              <tr key={idx}>
                <td>{p.promise}</td>
                <td>
                  <span className={`promise-badge ${statusInfo.className}`}>
                    {statusInfo.label}
                  </span>
                </td>
                <td>{p.evidence}</td>
                <td className="muted">{p.source}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
