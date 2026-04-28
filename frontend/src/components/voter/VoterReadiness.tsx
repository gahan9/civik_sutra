import { useState } from "react";
import { useTranslation } from "react-i18next";

import { BoothProcedure } from "./BoothProcedure";
import { CardApplication } from "./CardApplication";
import { ElectionDateLinks } from "./ElectionDateLinks";
import { EligibilityCheck } from "./EligibilityCheck";
import { VotingChecklist } from "./VotingChecklist";

export type VoterTab = "eligibility" | "checklist" | "apply" | "procedure";

type VoterReadinessProps = {
  initialTab?: VoterTab;
};

export function VoterReadiness({
  initialTab = "eligibility",
}: VoterReadinessProps = {}) {
  const [activeTab, setActiveTab] = useState<VoterTab>(initialTab ?? "eligibility");
  const { t } = useTranslation();

  const tabs: { id: VoterTab; label: string }[] = [
    { id: "eligibility", label: t("voter.eligibility") },
    { id: "checklist", label: t("voter.checklist") },
    { id: "apply", label: t("voter.applyCard") },
    { id: "procedure", label: t("voter.procedure") },
  ];

  return (
    <div className="shell">
      <section className="hero">
        <p className="eyebrow">{t("nav.voter")}</p>
        <h1>{t("voter.title")}</h1>
        <p>{t("voter.subtitle")}</p>
      </section>

      <ElectionDateLinks />

      <div className="voter-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={
              activeTab === tab.id ? "voter-tab voter-tab--active" : "voter-tab"
            }
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="voter-content">
        {activeTab === "eligibility" && <EligibilityCheck />}
        {activeTab === "checklist" && <VotingChecklist />}
        {activeTab === "apply" && <CardApplication />}
        {activeTab === "procedure" && <BoothProcedure />}
      </div>
    </div>
  );
}
