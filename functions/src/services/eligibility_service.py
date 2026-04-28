"""Local voter eligibility validation invoked from the Gemini AI coach.

Eligibility rules follow Article 326 of the Constitution and Section 16 of
the Representation of the People Act, 1950. The implementation is purely
deterministic — no external services are called — so the AI coach can rely
on the result inside its function-calling loop.
"""

from __future__ import annotations

from typing import Final, Literal
from datetime import date

CitizenshipStatus = Literal["indian", "nri", "foreign"]
ResidenceStatus = Literal["resident", "nri", "abroad"]

QUALIFYING_DAY: Final[tuple[int, int]] = (1, 1)


def check_voter_eligibility(
    age: int,
    citizenship: CitizenshipStatus,
    residence: ResidenceStatus = "resident",
    qualifying_year: int | None = None,
) -> dict[str, object]:
    """Return a structured eligibility verdict for the AI coach.

    Args:
        age: Voter's stated age in completed years.
        citizenship: ``indian``, ``nri`` or ``foreign``.
        residence: Residency status used to advise the correct registration
            form (Form 6 vs Form 6A).
        qualifying_year: Override the qualifying year (defaults to current
            calendar year). Useful for deterministic testing.

    Returns:
        A dictionary with ``eligible``, human-readable ``reason`` and an
        actionable ``next_step`` recommendation.

    """
    issues: list[str] = []

    if age < 18:
        issues.append(
            f"Minimum voting age is 18 on the qualifying date "
            f"(1 January {qualifying_year or date.today().year}); you are "
            f"{age}."
        )

    if citizenship == "foreign":
        issues.append(
            "Only Indian citizens may register on the electoral roll. "
            "Article 326 of the Constitution restricts the franchise to "
            "citizens of India."
        )

    if issues:
        return {
            "eligible": False,
            "reason": " ".join(issues),
            "next_step": _next_step_for_ineligible(age, citizenship),
        }

    if citizenship == "nri" or residence in {"nri", "abroad"}:
        return {
            "eligible": True,
            "reason": (
                "You meet the constitutional requirements. As an overseas "
                "Indian elector you must register using Form 6A and vote in "
                "person at your registered constituency."
            ),
            "next_step": (
                "File Form 6A on the NVSP portal (https://www.nvsp.in) and "
                "carry your Indian passport on polling day."
            ),
        }

    return {
        "eligible": True,
        "reason": (
            "You meet the constitutional requirements. Ensure your name is "
            "on the electoral roll and your EPIC details are correct before "
            "polling day."
        ),
        "next_step": (
            "Search electoralsearch.eci.gov.in by EPIC or details. If you "
            "are not listed, file Form 6 on https://www.nvsp.in."
        ),
    }


def _next_step_for_ineligible(
    age: int, citizenship: CitizenshipStatus
) -> str:
    if citizenship == "foreign":
        return (
            "Indian citizenship is mandatory. Acquire Indian citizenship "
            "under the Citizenship Act, 1955 before applying."
        )
    if age < 18:
        return (
            "Apply pre-emptively up to three months before turning 18 using "
            "Form 6 on https://www.nvsp.in so you are listed as soon as you "
            "qualify."
        )
    return (
        "Visit https://eci.gov.in for the latest eligibility framework and "
        "consult your Booth Level Officer (BLO) for personalised guidance."
    )
