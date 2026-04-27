import type {
  BoothVerificationResult,
  DirectionsRequest,
  DirectionsResult,
  NearbyRequest,
  NearbyResponse,
} from "../types/booth";

async function postJson<TRequest, TResponse>(
  path: string,
  payload: TRequest,
): Promise<TResponse> {
  const response = await fetch(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<TResponse>;
}

export function findNearbyBooths(
  request: NearbyRequest,
): Promise<NearbyResponse> {
  return postJson<NearbyRequest, NearbyResponse>("/booth/nearby", request);
}

export function getBoothDirections(
  request: DirectionsRequest,
): Promise<DirectionsResult> {
  return postJson<DirectionsRequest, DirectionsResult>(
    "/booth/directions",
    request,
  );
}

export async function verifyBoothAssignment(
  epicNumber: string,
): Promise<BoothVerificationResult> {
  const response = await fetch(
    `/booth/verify/${encodeURIComponent(epicNumber.trim())}`,
  );

  if (!response.ok) {
    throw new Error(`Verification failed with status ${response.status}`);
  }

  return response.json() as Promise<BoothVerificationResult>;
}
