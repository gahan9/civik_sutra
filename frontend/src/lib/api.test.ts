import { describe, expect, it, vi } from "vitest";

import { findNearbyBooths } from "./api";


describe("findNearbyBooths", () => {
  it("posts GPS coordinates to the booth endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        booths: [],
        suggested_visit_time: {
          window: "10:00-11:30",
          reason: "Low traffic",
        },
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await findNearbyBooths({ lat: 28.6139, lng: 77.209, radius_km: 5 });

    expect(fetchMock).toHaveBeenCalledWith(
      "/booth/nearby",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ lat: 28.6139, lng: 77.209, radius_km: 5 }),
      }),
    );
  });
});
