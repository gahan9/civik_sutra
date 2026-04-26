import { useState } from "react";

import { BoothFinder } from "./components/booth/BoothFinder";
import { CandidateSearch } from "./components/candidate/CandidateSearch";


type ActiveTab = "booth" | "candidate";

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("booth");

  return (
    <>
      <header className="shell">
        <nav className="nav-bar" aria-label="Main navigation">
          <button
            type="button"
            className={activeTab === "booth" ? "active" : ""}
            onClick={() => setActiveTab("booth")}
          >
            Booth Finder
          </button>
          <button
            type="button"
            className={activeTab === "candidate" ? "active" : ""}
            onClick={() => setActiveTab("candidate")}
          >
            Candidate Intelligence
          </button>
        </nav>
      </header>
      {activeTab === "booth" ? <BoothFinder /> : <CandidateSearch />}
    </>
  );
}
