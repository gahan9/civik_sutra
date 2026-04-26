export type Sentiment = "positive" | "negative" | "neutral";

export interface CandidateSearchRequest {
  constituency?: string;
  lat?: number;
  lng?: number;
}

export interface CompareRequest {
  candidate_ids: string[];
}

export interface CandidateSummary {
  id: string;
  name: string;
  party: string;
  party_symbol_url: string | null;
  education: string;
  age: number | null;
  criminal_cases: number;
  total_assets_inr: number;
  total_liabilities_inr: number;
  past_positions: string[];
}

export interface CandidateSearchResponse {
  constituency: string;
  election: string;
  candidates: CandidateSummary[];
}

export interface NewsItem {
  title: string;
  source: string;
  date: string;
  url: string | null;
  sentiment: Sentiment;
}

export interface SourceCitation {
  source: string;
  url: string | null;
  query: string | null;
}

export interface GroundingResult {
  recent_news: NewsItem[];
  achievements: string[];
  controversies: string[];
  social_media_presence: string | null;
  sources: SourceCitation[];
}

export interface CriminalCase {
  case_id: string | null;
  description: string;
  status: "pending" | "convicted" | "acquitted";
  court: string | null;
  ipc_sections: string[];
}

export interface AssetBreakdown {
  movable: number;
  immovable: number;
  vehicles: string[];
}

export interface BackgroundReport {
  candidate: CandidateSummary;
  grounding: GroundingResult;
  criminal_details: CriminalCase[];
  asset_breakdown: AssetBreakdown;
  source_urls: Record<string, string>;
}

export interface ComparisonResult {
  dimensions: string[];
  candidates: Record<string, Record<string, string>>;
  ai_analysis: string;
  ai_analysis_citations: SourceCitation[];
}
