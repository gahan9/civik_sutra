/**
 * Google Calendar "URL to create event" (template) links.
 * No API keys — suitable for public civic education (Nirvachan-style deep-linking).
 * @see https://calendar.google.com/calendar/u/0/r/eventedit (browser flow; template URLs use `action=TEMPLATE`)
 */
export type GoogleCalendarEventInput = {
  /** Event title (visible in Google Calendar) */
  title: string;
  /** Optional body — keep short; ECI is source of truth for real dates. */
  details?: string;
  /**
   * Window in UTC, format: YYYYMMDDTHHmmssZ (Google Calendar `dates` param).
   * These are **illustrative** slots; users should adjust to the official ECI / state schedule.
   */
  startUtcCompact: string;
  endUtcCompact: string;
};

/**
 * Returns a `calendar.google.com` link that opens the “Create event” screen prefilled.
 */
export function buildGoogleCalendarTemplateUrl(
  event: GoogleCalendarEventInput
): string {
  const { title, details = "", startUtcCompact, endUtcCompact } = event;
  const params = new URLSearchParams({
    action: "TEMPLATE",
    text: title,
    details,
    dates: `${startUtcCompact}/${endUtcCompact}`,
  });
  return `https://calendar.google.com/calendar/render?${params.toString()}`;
}

/** Default illustrative events for voter education (dates must be verified per election). */
export function defaultIndianElectionReminders(t: (key: string) => string): {
  id: string;
  title: string;
  details: string;
  startUtcCompact: string;
  endUtcCompact: string;
}[] {
  return [
    {
      id: "roll-check",
      title: t("calendar.ev1Title"),
      details: t("calendar.ev1Details"),
      startUtcCompact: "20260115T043000Z",
      endUtcCompact: "20260115T050000Z",
    },
    {
      id: "poll-day",
      title: t("calendar.ev2Title"),
      details: t("calendar.ev2Details"),
      startUtcCompact: "20260420T010000Z",
      endUtcCompact: "20260420T100000Z",
    },
    {
      id: "counting",
      title: t("calendar.ev3Title"),
      details: t("calendar.ev3Details"),
      startUtcCompact: "20260523T043000Z",
      endUtcCompact: "20260523T120000Z",
    },
  ];
}

/**
 * Convert an ISO ``YYYY-MM-DD`` date into Google Calendar's compact UTC
 * format ``YYYYMMDDTHHmmssZ``. The optional ``time`` selects the
 * conventional anchor (start of polling day vs. end of polling day).
 */
export function isoDateToCalendarCompact(
  isoDate: string,
  time: "start" | "end" = "start"
): string {
  const trimmed = isoDate.trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return trimmed;
  }
  const [year, month, day] = trimmed.split("-");
  const suffix = time === "start" ? "T010000Z" : "T133000Z";
  return `${year}${month}${day}${suffix}`;
}
