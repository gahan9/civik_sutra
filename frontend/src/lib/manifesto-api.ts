import type {
  ManifestoCompareRequest,
  ManifestoComparison,
} from "../types/manifesto";

export async function compareManifestos(
  request: ManifestoCompareRequest,
): Promise<ManifestoComparison> {
  const response = await fetch("/manifesto/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(
      `Manifesto comparison failed with status ${response.status}`,
    );
  }

  return response.json() as Promise<ManifestoComparison>;
}
