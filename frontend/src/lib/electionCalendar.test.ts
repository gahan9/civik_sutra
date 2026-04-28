import { describe, expect, it } from "vitest";

import {
  buildGoogleCalendarTemplateUrl,
  isoDateToCalendarCompact,
} from "./electionCalendar";

describe("buildGoogleCalendarTemplateUrl", () => {
  it("builds a Google Calendar template URL with encoded params", () => {
    const url = buildGoogleCalendarTemplateUrl({
      title: "Test event",
      details: "Line1\nLine2",
      startUtcCompact: "20260101T100000Z",
      endUtcCompact: "20260101T110000Z",
    });
    expect(url).toMatch(/^https:\/\/calendar\.google\.com\/calendar\/render\?/u);
    expect(url).toContain("action=TEMPLATE");
    expect(url).toMatch(/text=Test(\+|%20)event/u);
    expect(url).toContain("dates=20260101T100000Z%2F20260101T110000Z");
  });
});

describe("isoDateToCalendarCompact", () => {
  it("converts an ISO date to start-of-day UTC compact format", () => {
    expect(isoDateToCalendarCompact("2026-04-19", "start")).toBe("20260419T010000Z");
  });

  it("converts an ISO date to end-of-day UTC compact format", () => {
    expect(isoDateToCalendarCompact("2026-04-19", "end")).toBe("20260419T133000Z");
  });

  it("returns the input unchanged when the format is unexpected", () => {
    expect(isoDateToCalendarCompact("not-a-date")).toBe("not-a-date");
  });
});
