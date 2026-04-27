import { useState } from "react";
import { useTranslation } from "react-i18next";

import { BoothFinder } from "./components/booth/BoothFinder";
import { CandidateSearch } from "./components/candidate/CandidateSearch";
import { AssistantChat } from "./components/chat/AssistantChat";
import { ManifestoComparison } from "./components/manifesto/ManifestoComparison";
import { LanguageSelector } from "./components/ui/LanguageSelector";
import { VoterReadiness } from "./components/voter/VoterReadiness";

type ActiveTab = "booth" | "candidate" | "manifesto" | "chat" | "voter";

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("booth");
  const { t } = useTranslation();

  return (
    <>
      <header className="shell">
        <div className="header-top">
          <LanguageSelector />
        </div>
        <nav className="nav-bar" aria-label="Main navigation">
          <button
            type="button"
            className={activeTab === "booth" ? "active" : ""}
            onClick={() => setActiveTab("booth")}
          >
            {t("nav.booth")}
          </button>
          <button
            type="button"
            className={activeTab === "candidate" ? "active" : ""}
            onClick={() => setActiveTab("candidate")}
          >
            {t("nav.candidates")}
          </button>
          <button
            type="button"
            className={activeTab === "manifesto" ? "active" : ""}
            onClick={() => setActiveTab("manifesto")}
          >
            {t("nav.manifesto")}
          </button>
          <button
            type="button"
            className={activeTab === "voter" ? "active" : ""}
            onClick={() => setActiveTab("voter")}
          >
            {t("nav.voter")}
          </button>
          <button
            type="button"
            className={activeTab === "chat" ? "active" : ""}
            onClick={() => setActiveTab("chat")}
          >
            {t("nav.chat")}
          </button>
        </nav>
      </header>
      {activeTab === "booth" && <BoothFinder />}
      {activeTab === "candidate" && <CandidateSearch />}
      {activeTab === "manifesto" && <ManifestoComparison />}
      {activeTab === "voter" && <VoterReadiness />}
      {activeTab === "chat" && <AssistantChat />}
    </>
  );
}
