import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import {
  buildGoogleCalendarTemplateUrl,
  defaultIndianElectionReminders,
  isoDateToCalendarCompact,
} from "../../lib/electionCalendar";
import { getElectionTimeline, type ElectionTimelineEvent } from "../../lib/chat-api";

type CalendarRow = {
  id: string;
  title: string;
  details: string;
  startUtcCompact: string;
  endUtcCompact: string;
  source?: { label: string; url: string };
};

/**
 * Google Calendar deep-links for key milestones. Pulls live data from the
 * `/assistant/timeline` endpoint and gracefully degrades to the static
 * placeholders when the API is unreachable so the user always sees actionable
 * reminders.
 */
export function ElectionDateLinks() {
  const { t } = useTranslation();
  const [rows, setRows] = useState<CalendarRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load(): Promise<void> {
      try {
        const events = await getElectionTimeline();
        if (cancelled) return;
        if (events.length > 0) {
          setRows(events.map(eventToCalendarRow));
          setIsLive(true);
          return;
        }
      } catch {
        if (cancelled) return;
      }
      setRows(defaultIndianElectionReminders(t));
      setIsLive(false);
    }

    void load().finally(() => {
      if (!cancelled) {
        setLoading(false);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [t]);

  return (
    <section className="election-dates" aria-labelledby="election-dates-title">
      <h2 id="election-dates-title" className="election-dates__title">
        {t("calendar.title")}
        {isLive && (
          <span
            className="election-dates__badge"
            aria-label={t("calendar.liveSourceLabel")}
          >
            {" "}
            • {t("calendar.liveSourceLabel")}
          </span>
        )}
      </h2>
      <p className="election-dates__sub">{t("calendar.subtitle")}</p>
      {loading ? (
        <p className="election-dates__loading">{t("calendar.loadingLive")}</p>
      ) : (
        <ul className="election-dates__list">
          {rows.map((row) => {
            const href = buildGoogleCalendarTemplateUrl({
              title: row.title,
              details: row.details,
              startUtcCompact: row.startUtcCompact,
              endUtcCompact: row.endUtcCompact,
            });
            return (
              <li key={row.id}>
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="election-dates__link"
                >
                  {t("calendar.addToCalendar")}: {row.title}
                </a>
                {row.source && (
                  <span className="election-dates__source">
                    {" "}
                    —{" "}
                    <a href={row.source.url} target="_blank" rel="noopener noreferrer">
                      {row.source.label}
                    </a>
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

function eventToCalendarRow(event: ElectionTimelineEvent): CalendarRow {
  return {
    id: event.id,
    title: event.title,
    details: `${event.description}\nStage: ${event.stage}`,
    startUtcCompact: isoDateToCalendarCompact(event.starts_on, "start"),
    endUtcCompact: isoDateToCalendarCompact(event.ends_on, "end"),
    source: { label: event.source, url: event.source_url },
  };
}
