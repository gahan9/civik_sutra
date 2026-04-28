const PROCEDURE_STEPS = [
  {
    step: 1,
    title: "Arrive & Queue",
    description:
      "Arrive at your assigned polling booth during polling hours (usually 7 AM - 6 PM). Join the queue for your booth number.",
    icon: "🏫",
  },
  {
    step: 2,
    title: "Identity Verification",
    description:
      "Show your valid photo ID to the presiding officer. They will verify your name against the electoral roll.",
    icon: "🪪",
  },
  {
    step: 3,
    title: "Ink Mark & Ballot Slip",
    description:
      "Your left index finger will be marked with indelible ink. You'll receive a ballot slip with your serial number.",
    icon: "✋",
  },
  {
    step: 4,
    title: "Enter Voting Compartment",
    description:
      "Enter the voting compartment ALONE. No phones, cameras, or companions allowed inside (PWD voters excepted).",
    icon: "🚪",
  },
  {
    step: 5,
    title: "Cast Your Vote on EVM",
    description:
      "The Electronic Voting Machine (EVM) has a list of candidates with party symbols. Press the blue button next to your chosen candidate.",
    icon: "🗳️",
  },
  {
    step: 6,
    title: "Verify on VVPAT",
    description:
      "After pressing the button, you'll hear a BEEP. The VVPAT machine will display a printed slip showing the candidate name and symbol for 7 seconds. Verify it matches your choice.",
    icon: "✅",
  },
  {
    step: 7,
    title: "Exit",
    description:
      "Once verified, exit the voting compartment. Your vote has been cast. Do NOT discuss your vote with anyone inside the booth premises.",
    icon: "🚶",
  },
];

export function BoothProcedure() {
  return (
    <div className="voter-section">
      <h2>Voting Procedure at the Booth</h2>
      <p className="muted">
        Step-by-step guide to casting your vote using EVM and VVPAT.
      </p>

      <div className="procedure-steps">
        {PROCEDURE_STEPS.map((step) => (
          <div key={step.step} className="procedure-step">
            <div className="procedure-icon">{step.icon}</div>
            <div className="procedure-content">
              <h3>
                <span className="procedure-num">Step {step.step}</span>
                {step.title}
              </h3>
              <p>{step.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="voter-info-box">
        <h3>What is NOTA?</h3>
        <p>
          NOTA (None Of The Above) is the last option on the EVM. If you feel no
          candidate deserves your vote, you can press NOTA. While NOTA votes are
          counted, even if NOTA gets the most votes, the candidate with the highest
          regular votes wins.
        </p>
      </div>

      <div className="voter-info-box">
        <h3>About EVM & VVPAT</h3>
        <p>
          <strong>EVM (Electronic Voting Machine)</strong> stores your vote
          electronically. It runs on battery, cannot be connected to any network, and
          stores votes in a tamper-proof chip.
        </p>
        <p>
          <strong>VVPAT (Voter Verifiable Paper Audit Trail)</strong> prints a paper
          slip after each vote, allowing you to verify that your vote was recorded
          correctly. The slip drops into a sealed box for potential audit.
        </p>
      </div>
    </div>
  );
}
