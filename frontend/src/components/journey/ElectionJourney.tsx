import { useTranslation } from "react-i18next";

import { type JourneyTab } from "../../types/journey";

type ElectionJourneyProps = {
  active: JourneyTab;
  onSelect: (tab: JourneyTab) => void;
};

type StageMeta = {
  id: JourneyTab;
  labelKey: string;
  descriptionKey: string;
};

const STAGES: readonly StageMeta[] = [
  {
    id: "eligibility",
    labelKey: "journey.stepEligibility",
    descriptionKey: "journey.descEligibility",
  },
  {
    id: "register",
    labelKey: "journey.stepRegister",
    descriptionKey: "journey.descRegister",
  },
  {
    id: "research",
    labelKey: "journey.stepResearch",
    descriptionKey: "journey.descResearch",
  },
  {
    id: "compare",
    labelKey: "journey.stepCompare",
    descriptionKey: "journey.descCompare",
  },
  {
    id: "locate",
    labelKey: "journey.stepLocate",
    descriptionKey: "journey.descLocate",
  },
  {
    id: "vote",
    labelKey: "journey.stepVote",
    descriptionKey: "journey.descVote",
  },
  {
    id: "chat",
    labelKey: "journey.stepChat",
    descriptionKey: "journey.descChat",
  },
];

/**
 * Linear seven-stage voter journey: a guided civic flow from "Am I eligible?"
 * to "Cast my vote" with an always-available AI coach as the seventh stage.
 *
 * Each stage exposes a numbered button plus a short description so the path is
 * legible to first-time voters who do not yet know the formal vocabulary.
 */
export function ElectionJourney({ active, onSelect }: ElectionJourneyProps) {
  const { t } = useTranslation();
  const activeIndex = STAGES.findIndex((stage) => stage.id === active);

  return (
    <div className="election-journey" role="region" aria-label={t("journey.label")}>
      <ol className="election-journey__steps">
        {STAGES.map((stage, i) => {
          const isActive = active === stage.id;
          const isCompleted = activeIndex > i;
          const buttonClass = [
            "election-journey__btn",
            isActive ? "election-journey__btn--active" : "",
            isCompleted ? "election-journey__btn--done" : "",
          ]
            .filter(Boolean)
            .join(" ");

          return (
            <li key={stage.id} className="election-journey__item">
              <button
                type="button"
                className={buttonClass}
                onClick={() => {
                  onSelect(stage.id);
                }}
                aria-current={isActive ? "step" : undefined}
                title={t(stage.descriptionKey)}
              >
                <span className="election-journey__n" aria-hidden="true">
                  {i + 1}
                </span>
                <span className="election-journey__label">{t(stage.labelKey)}</span>
              </button>
              {i < STAGES.length - 1 && (
                <span className="election-journey__sep" aria-hidden="true">
                  →
                </span>
              )}
            </li>
          );
        })}
      </ol>
      <p className="election-journey__hint" aria-live="polite">
        {activeIndex >= 0 ? t(STAGES[activeIndex].descriptionKey) : ""}
      </p>
    </div>
  );
}
