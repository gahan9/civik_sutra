import { useState } from "react";

import { BoothProcedure } from "./BoothProcedure";
import { CardApplication } from "./CardApplication";
import { EligibilityCheck } from "./EligibilityCheck";
import { VotingChecklist } from "./VotingChecklist";


type VoterTab = "eligibility" | "checklist" | "apply" | "procedure";

const TABS: { id: VoterTab; label: string }[] = [
  { id: "eligibility", label: "Am I Eligible?" },
  { id: "checklist", label: "Voting Checklist" },
  { id: "apply", label: "Apply for Voter ID" },
  { id: "procedure", label: "Booth Procedure" },
];

export function VoterReadiness() {
  const [activeTab, setActiveTab] = useState<VoterTab>("eligibility");

  return (
    <div className="shell">
      <section className="hero">
        <p className="eyebrow">Voter Readiness</p>
        <h1>Be Prepared to Vote</h1>
        <p>
          Everything you need to know before, during, and after voting.
          Check your eligibility, prepare your documents, and understand the process.
        </p>
      </section>

      <div className="voter-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={activeTab === tab.id ? "voter-tab voter-tab--active" : "voter-tab"}
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
