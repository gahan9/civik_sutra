import { useCallback, useState } from "react";

import { INDIAN_STATES, NVSP_URLS } from "../../data/voter-readiness";

type CitizenType = "citizen" | "nri" | "non_citizen" | "";
type RegisteredType = "yes" | "no" | "not_sure" | "";

interface EligibilityResult {
  eligible: boolean;
  reason: string;
  action?: "register" | "check" | "ready" | "nri";
}

function checkEligibility(
  age: number,
  citizen: CitizenType,
  registered: RegisteredType,
): EligibilityResult | null {
  if (!citizen) return null;

  if (age < 18) {
    return {
      eligible: false,
      reason:
        "Must be 18 years or older on the qualifying date (January 1 of the election year).",
    };
  }
  if (citizen === "non_citizen") {
    return {
      eligible: false,
      reason: "Must be an Indian citizen to vote in Indian elections.",
    };
  }
  if (citizen === "nri") {
    return {
      eligible: true,
      reason:
        "NRIs can vote! Register as an overseas voter via Form 6A on the NVSP portal.",
      action: "nri",
    };
  }
  if (registered === "no") {
    return {
      eligible: true,
      reason:
        "You are eligible but need to register first. Apply at least 15 days before election date.",
      action: "register",
    };
  }
  if (registered === "not_sure") {
    return {
      eligible: true,
      reason:
        "Verify your registration on the NVSP portal or ECI Electoral Search.",
      action: "check",
    };
  }
  if (registered === "yes") {
    return {
      eligible: true,
      reason: "You are registered and ready to vote!",
      action: "ready",
    };
  }
  return null;
}

export function EligibilityCheck() {
  const [age, setAge] = useState("");
  const [citizen, setCitizen] = useState<CitizenType>("");
  const [registered, setRegistered] = useState<RegisteredType>("");
  const [state, setState] = useState("");
  const [result, setResult] = useState<EligibilityResult | null>(null);

  const handleCheck = useCallback(() => {
    const ageNum = parseInt(age, 10);
    if (isNaN(ageNum) || !citizen) return;
    setResult(checkEligibility(ageNum, citizen, registered));
  }, [age, citizen, registered]);

  return (
    <div className="voter-section">
      <h2>Am I Eligible to Vote?</h2>
      <p className="muted">Answer a few questions to find out.</p>

      <div className="voter-form">
        <div className="voter-field">
          <label htmlFor="age-input">What is your age?</label>
          <input
            id="age-input"
            type="number"
            min="1"
            max="150"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            placeholder="Enter your age"
          />
        </div>

        <div className="voter-field">
          <fieldset>
            <legend>Are you an Indian citizen?</legend>
            <div className="voter-radio-group">
              {(["citizen", "nri", "non_citizen"] as CitizenType[]).map((val) => (
                <label key={val} className="voter-radio">
                  <input
                    type="radio"
                    name="citizen"
                    value={val}
                    checked={citizen === val}
                    onChange={() => setCitizen(val)}
                  />
                  {val === "citizen" ? "Yes" : val === "nri" ? "NRI" : "No"}
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        <div className="voter-field">
          <fieldset>
            <legend>Are you registered as a voter?</legend>
            <div className="voter-radio-group">
              {(["yes", "no", "not_sure"] as RegisteredType[]).map((val) => (
                <label key={val} className="voter-radio">
                  <input
                    type="radio"
                    name="registered"
                    value={val}
                    checked={registered === val}
                    onChange={() => setRegistered(val)}
                  />
                  {val === "not_sure"
                    ? "Not sure"
                    : val.charAt(0).toUpperCase() + val.slice(1)}
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        <div className="voter-field">
          <label htmlFor="state-select">State of residence:</label>
          <select
            id="state-select"
            value={state}
            onChange={(e) => setState(e.target.value)}
          >
            <option value="">Select state</option>
            {INDIAN_STATES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <button type="button" onClick={handleCheck} disabled={!age || !citizen}>
          Check Eligibility
        </button>
      </div>

      {result && (
        <div
          className={
            result.eligible
              ? "voter-result voter-result--eligible"
              : "voter-result voter-result--ineligible"
          }
        >
          <h3>
            {result.eligible
              ? "You ARE eligible to vote!"
              : "You are not eligible to vote"}
          </h3>
          <p>{result.reason}</p>

          {result.action === "register" && (
            <div className="card-actions">
              <a
                href={NVSP_URLS.newRegistration}
                target="_blank"
                rel="noopener noreferrer"
                className="button-link"
              >
                Apply for Voter ID
              </a>
            </div>
          )}

          {result.action === "check" && (
            <div className="card-actions">
              <a
                href={NVSP_URLS.searchName}
                target="_blank"
                rel="noopener noreferrer"
                className="button-link"
              >
                Check Registration
              </a>
            </div>
          )}

          {result.action === "nri" && (
            <div className="card-actions">
              <a
                href={NVSP_URLS.portal}
                target="_blank"
                rel="noopener noreferrer"
                className="button-link"
              >
                NVSP Portal (Form 6A)
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
