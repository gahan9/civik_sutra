import { useCallback, useState } from "react";

import { APPLICATION_STEPS, NVSP_URLS } from "../../data/voter-readiness";


export function CardApplication() {
  const [currentStep, setCurrentStep] = useState(0);

  const goNext = useCallback(() => {
    setCurrentStep((prev) => Math.min(prev + 1, APPLICATION_STEPS.length - 1));
  }, []);

  const goPrev = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const step = APPLICATION_STEPS[currentStep];

  return (
    <div className="voter-section">
      <h2>Apply for Voter ID (EPIC)</h2>

      <div className="step-progress">
        {APPLICATION_STEPS.map((s, idx) => (
          <button
            key={s.step}
            type="button"
            className={
              idx === currentStep
                ? "step-dot step-dot--active"
                : idx < currentStep
                  ? "step-dot step-dot--done"
                  : "step-dot"
            }
            onClick={() => setCurrentStep(idx)}
            aria-label={`Step ${s.step}: ${s.title}`}
          >
            {idx < currentStep ? "✓" : s.step}
          </button>
        ))}
      </div>

      <div className="step-card">
        <div className="step-card-header">
          <span className="step-number">Step {step.step} of {APPLICATION_STEPS.length}</span>
          <h3>{step.title}</h3>
        </div>

        <p>{step.description}</p>

        {"requiredDocs" in step && step.requiredDocs && (
          <div className="step-docs">
            <h4>Required Documents:</h4>
            <ul>
              {step.requiredDocs.map((doc) => (
                <li key={doc}>{doc}</li>
              ))}
            </ul>
          </div>
        )}

        {"timeline" in step && step.timeline && (
          <p className="step-timeline">
            <strong>Timeline:</strong> {step.timeline}
          </p>
        )}

        {"url" in step && step.url && (
          <a
            href={step.url}
            target="_blank"
            rel="noopener noreferrer"
            className="button-link secondary"
          >
            Open Portal
          </a>
        )}

        <div className="step-nav">
          <button
            type="button"
            className="secondary"
            onClick={goPrev}
            disabled={currentStep === 0}
          >
            Previous
          </button>
          <button
            type="button"
            onClick={goNext}
            disabled={currentStep === APPLICATION_STEPS.length - 1}
          >
            Next Step
          </button>
        </div>
      </div>

      <div className="step-extra">
        <h3>Important Dates</h3>
        <ul>
          <li>Apply at least 15 days before election date</li>
          <li>Processing: 7-15 working days</li>
          <li>Track status on NVSP portal</li>
        </ul>

        <div className="card-actions" style={{ marginTop: "0.75rem" }}>
          <a
            href={NVSP_URLS.trackApplication}
            target="_blank"
            rel="noopener noreferrer"
            className="button-link secondary"
          >
            Track Application Status
          </a>
        </div>
      </div>
    </div>
  );
}
