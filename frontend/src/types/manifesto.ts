export type PromiseStatus = "fulfilled" | "partial" | "not_met" | "ongoing";

export interface ManifestoCompareRequest {
  party_names: string[];
  categories?: string[] | null;
  include_past_promises: boolean;
}

export interface ManifestoSource {
  party: string;
  manifesto_url: string | null;
}

export interface PromiseTracker {
  promise: string;
  status: PromiseStatus;
  evidence: string;
  source: string;
}

export interface ManifestoComparison {
  parties: string[];
  categories: Record<string, Record<string, string[]>>;
  ai_analysis: string;
  past_promises: Record<string, PromiseTracker[]> | null;
  sources: ManifestoSource[];
}
