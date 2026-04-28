"""Static election timeline data exposed via the Gemini ``get_election_timeline`` tool.

The dates here are illustrative anchors used by the AI coach when a voter
asks "when is the election?" and similar. The dataset is intentionally
treated as authoritative for *educational* purposes only — production
deployments must override it with the live ECI schedule once announced.
"""

from __future__ import annotations

from typing import Final

ElectionEvent = dict[str, str]

ELECTION_EVENTS: Final[list[ElectionEvent]] = [
    {
        "id": "roll-revision-window",
        "title": "Voter Roll Special Summary Revision",
        "stage": "Pre-Election",
        "starts_on": "2025-10-29",
        "ends_on": "2025-12-09",
        "description": (
            "Submit Form 6/8/8A on NVSP. Confirm your name, polling station "
            "and EPIC number before the rolls are frozen for the next "
            "election cycle."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "model-code-of-conduct",
        "title": "Model Code of Conduct in Force",
        "stage": "Election Notification",
        "starts_on": "2026-03-15",
        "ends_on": "2026-06-04",
        "description": (
            "From the date the ECI announces the schedule until results are "
            "declared, the Model Code of Conduct binds parties, candidates "
            "and the ruling government."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "nomination-window",
        "title": "Candidate Nominations Open",
        "stage": "Nomination",
        "starts_on": "2026-03-20",
        "ends_on": "2026-04-04",
        "description": (
            "Candidates file Form 2A/2B affidavits with the Returning "
            "Officer. Affidavits become public on the ECI website and "
            "MyNeta.info on the closing date."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "phase-1-poll",
        "title": "Phase 1 Polling Day",
        "stage": "Polling",
        "starts_on": "2026-04-19",
        "ends_on": "2026-04-19",
        "description": (
            "Polling stations open from 7:00 AM to 6:00 PM. Carry your EPIC "
            "or accepted alternate ID and avoid mobile phones inside the "
            "polling compartment."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "phase-final-poll",
        "title": "Final Phase Polling Day",
        "stage": "Polling",
        "starts_on": "2026-05-30",
        "ends_on": "2026-05-30",
        "description": (
            "Final phase of multi-phase polling. EVMs are sealed and stored "
            "in strong rooms under continuous video surveillance until "
            "counting day."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "counting-day",
        "title": "Counting Day & Results",
        "stage": "Result",
        "starts_on": "2026-06-04",
        "ends_on": "2026-06-04",
        "description": (
            "Counting begins at 8:00 AM with postal ballots followed by EVM "
            "rounds. Results are declared on results.eci.gov.in and the "
            "winning candidate receives Form 21C."
        ),
        "source": "Election Commission of India",
        "source_url": "https://results.eci.gov.in",
    },
    {
        "id": "petition-deadline",
        "title": "Election Petition Window Closes",
        "stage": "Post-Result",
        "starts_on": "2026-06-04",
        "ends_on": "2026-07-19",
        "description": (
            "An election petition must be filed in the relevant High Court "
            "within 45 days of the result under Section 81 of the "
            "Representation of the People Act, 1951."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
]
