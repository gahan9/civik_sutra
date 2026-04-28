export type JourneyTab =
  | "eligibility"
  | "register"
  | "research"
  | "compare"
  | "locate"
  | "vote"
  | "chat";

export const JOURNEY_STAGES: readonly JourneyTab[] = [
  "eligibility",
  "register",
  "research",
  "compare",
  "locate",
  "vote",
  "chat",
] as const;
