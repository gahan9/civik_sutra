import { FormEvent, useState } from "react";

import { searchCandidates } from "../../lib/candidate-api";
import type { CandidateSearchResponse, CandidateSummary } from "../../types/candidate";
import { useGeolocation } from "../../hooks/useGeolocation";
import { CandidateCard } from "./CandidateCard";
import { CandidateCompare } from "./CandidateCompare";
import { CandidateProfile } from "./CandidateProfile";


type View = "search" | "profile" | "compare";
const MAX_COMPARE = 4;

export function CandidateSearch() {
  const geolocation = useGeolocation();

  const [query, setQuery] = useState("");
  const [searchResult, setSearchResult] = useState<CandidateSearchResponse | null>(null);
  const [selected, setSelected] = useState<CandidateSummary[]>([]);
  const [view, setView] = useState<View>("search");
  const [profileCandidate, setProfileCandidate] = useState<CandidateSummary | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (query.trim().length < 2) {
      setError("Enter at least 2 characters for constituency search.");
      return;
    }
    try {
      setStatus("Searching candidates...");
      setError(null);
      const result = await searchCandidates({ constituency: query.trim() });
      setSearchResult(result);
      setSelected([]);
      setView("search");
    } catch {
      setError("Unable to search candidates. Please try again.");
    } finally {
      setStatus(null);
    }
  }

  async function handleUseLocation() {
    const location = await geolocation.requestLocation();
    if (!location) return;

    try {
      setStatus("Finding candidates near you...");
      setError(null);
      const result = await searchCandidates({
        lat: location.lat,
        lng: location.lng,
      });
      setSearchResult(result);
      setSelected([]);
      setView("search");
    } catch {
      setError("Unable to find candidates for your location.");
    } finally {
      setStatus(null);
    }
  }

  function handleSelect(candidate: CandidateSummary) {
    setSelected((prev) => {
      const exists = prev.some((c) => c.id === candidate.id);
      if (exists) return prev.filter((c) => c.id !== candidate.id);
      if (prev.length >= MAX_COMPARE) return prev;
      return [...prev, candidate];
    });
  }

  function handleProfile(candidate: CandidateSummary) {
    setProfileCandidate(candidate);
    setView("profile");
  }

  function handleCompare() {
    if (selected.length >= 2) {
      setView("compare");
    }
  }

  function handleBack() {
    setView("search");
    setProfileCandidate(null);
  }

  const candidates = searchResult?.candidates ?? [];

  if (view === "profile" && profileCandidate) {
    return (
      <main className="shell">
        <CandidateProfile candidate={profileCandidate} onBack={handleBack} />
      </main>
    );
  }

  if (view === "compare" && selected.length >= 2) {
    return (
      <main className="shell">
        <CandidateCompare candidates={selected} onBack={handleBack} />
      </main>
    );
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">CivikSutra Candidate Intelligence</p>
        <h1>Research Your Candidates</h1>
        <p>
          Get background checks, criminal records, asset declarations, and
          AI-powered comparative analysis for candidates in your constituency.
        </p>
        <div className="impact-grid" aria-label="Feature highlights">
          <span>Background search</span>
          <span>Criminal record check</span>
          <span>Asset transparency</span>
          <span>AI comparison</span>
        </div>
      </section>

      <section className="manual-search" aria-labelledby="candidate-search-title">
        <h2 id="candidate-search-title">Find Your Candidates</h2>
        <form onSubmit={(event) => void handleSearch(event)}>
          <label htmlFor="constituency-search">Constituency name</label>
          <div className="input-row">
            <input
              id="constituency-search"
              name="constituency-search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="e.g. South Delhi, Mumbai North"
            />
            <button type="submit">Search</button>
          </div>
        </form>
        <div className="hero-actions" style={{ marginTop: "0.75rem" }}>
          <button
            className="secondary"
            type="button"
            onClick={() => void handleUseLocation()}
          >
            {geolocation.loading
              ? "Detecting location..."
              : "Use my location"}
          </button>
        </div>
        {geolocation.error ? <p className="alert">{geolocation.error}</p> : null}
      </section>

      {error ? <p className="alert">{error}</p> : null}
      {status ? <p className="status">{status}</p> : null}

      {searchResult ? (
        <section className="candidate-results" aria-labelledby="results-title">
          <div className="section-heading">
            <h2 id="results-title">
              {searchResult.constituency} ({candidates.length} candidates)
            </h2>
            <p className="muted">{searchResult.election}</p>
          </div>

          <div className="candidate-list">
            {candidates.map((candidate) => (
              <CandidateCard
                key={candidate.id}
                candidate={candidate}
                selected={selected.some((s) => s.id === candidate.id)}
                onSelect={handleSelect}
                onProfile={handleProfile}
              />
            ))}
          </div>

          <div className="compare-bar">
            <button
              type="button"
              onClick={handleCompare}
              disabled={selected.length < 2}
            >
              Compare Selected ({selected.length}/{MAX_COMPARE})
            </button>
            {selected.length === 1 ? (
              <p className="muted">Select at least 2 candidates to compare</p>
            ) : null}
            {selected.length >= MAX_COMPARE ? (
              <p className="muted">Maximum {MAX_COMPARE} candidates for comparison</p>
            ) : null}
          </div>

          <p className="source-note">
            Data sourced from MyNeta.info and ECI affidavits. Recent news via
            Gemini grounding search. Always verify with official records.
          </p>
        </section>
      ) : (
        <section className="candidate-results">
          <p className="empty-state">
            Search by constituency name or use your location to discover
            candidates contesting in your area.
          </p>
        </section>
      )}
    </main>
  );
}
