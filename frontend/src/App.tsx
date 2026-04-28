import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { BoothFinder } from "./components/booth/BoothFinder";
import { CandidateSearch } from "./components/candidate/CandidateSearch";
import { AssistantChat } from "./components/chat/AssistantChat";
import { ElectionJourney } from "./components/journey/ElectionJourney";
import { type JourneyTab } from "./types/journey";
import { ManifestoComparison } from "./components/manifesto/ManifestoComparison";
import { LanguageSelector } from "./components/ui/LanguageSelector";
import { TrustBanner } from "./components/ui/TrustBanner";
import { VoterReadiness, type VoterTab } from "./components/voter/VoterReadiness";

type ActiveTab = JourneyTab;

type NavEntry = {
  id: JourneyTab;
  labelKey: string;
};

const NAV_ENTRIES: readonly NavEntry[] = [
  { id: "eligibility", labelKey: "nav.eligibility" },
  { id: "register", labelKey: "nav.register" },
  { id: "research", labelKey: "nav.research" },
  { id: "compare", labelKey: "nav.compare" },
  { id: "locate", labelKey: "nav.locate" },
  { id: "vote", labelKey: "nav.vote" },
  { id: "chat", labelKey: "nav.chat" },
];

const VOTER_TAB_BY_STAGE: Partial<Record<JourneyTab, VoterTab>> = {
  eligibility: "eligibility",
  register: "apply",
  vote: "checklist",
};

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("eligibility");
  const { t } = useTranslation();

  const voterInitialTab = useMemo<VoterTab | undefined>(() => {
    return VOTER_TAB_BY_STAGE[activeTab];
  }, [activeTab]);

  return (
    <>
      <header className="shell">
        <div className="header-top">
          <LanguageSelector />
        </div>
        <ElectionJourney
          active={activeTab}
          onSelect={(tab) => {
            setActiveTab(tab);
          }}
        />
        <nav className="nav-bar" aria-label="Main navigation">
          {NAV_ENTRIES.map((entry) => (
            <button
              key={entry.id}
              type="button"
              className={activeTab === entry.id ? "active" : ""}
              onClick={() => setActiveTab(entry.id)}
              aria-current={activeTab === entry.id ? "page" : undefined}
            >
              {t(entry.labelKey)}
            </button>
          ))}
        </nav>
      </header>
      <TrustBanner />
      <main className="app-main" id="main-content" tabIndex={-1}>
        {(activeTab === "eligibility" ||
          activeTab === "register" ||
          activeTab === "vote") && (
          <VoterReadiness
            key={voterInitialTab ?? "voter-default"}
            initialTab={voterInitialTab}
          />
        )}
        {activeTab === "research" && <CandidateSearch />}
        {activeTab === "compare" && <ManifestoComparison />}
        {activeTab === "locate" && <BoothFinder />}
        {activeTab === "chat" && <AssistantChat />}
      </main>
    </>
  );
}
