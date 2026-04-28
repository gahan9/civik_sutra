import type {
  BackgroundReport,
  CandidateSearchRequest,
  CandidateSearchResponse,
  CompareRequest,
  ComparisonResult,
} from "../types/candidate";

async function postJson<TRequest, TResponse>(
  path: string,
  payload: TRequest
): Promise<TResponse> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<TResponse>;
}

export function searchCandidates(
  request: CandidateSearchRequest
): Promise<CandidateSearchResponse> {
  return postJson<CandidateSearchRequest, CandidateSearchResponse>(
    "/candidate/search",
    request
  );
}

export async function getCandidateBackground(
  candidateId: string
): Promise<BackgroundReport> {
  const response = await fetch(
    `/candidate/${encodeURIComponent(candidateId)}/background`
  );

  if (!response.ok) {
    throw new Error(`Background check failed with status ${response.status}`);
  }

  return response.json() as Promise<BackgroundReport>;
}

export function compareCandidates(request: CompareRequest): Promise<ComparisonResult> {
  return postJson<CompareRequest, ComparisonResult>("/candidate/compare", request);
}
