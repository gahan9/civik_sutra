export interface LatLng {
  lat: number;
  lng: number;
}

export interface ChatRequest {
  message: string;
  session_id: string;
  language: string;
  location?: LatLng | null;
}

export interface SourceCitation {
  source: string;
  url: string | null;
}

export interface ToolCallRecord {
  tool_name: string;
  args: Record<string, unknown>;
  result_summary: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  citations: SourceCitation[];
  tokens_used: number;
  tool_calls: ToolCallRecord[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  originalContent?: string;
  citations?: SourceCitation[];
  tool_calls?: ToolCallRecord[];
}
