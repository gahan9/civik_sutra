"""Defensive sanitisation for free-text inputs before they reach the LLM.

The goal is *not* to invent a perfect prompt-injection filter — that is an
unsolved problem — but to remove obvious overrides such as "ignore previous
instructions" and to clamp the message length so a single voter cannot
exhaust our token budget. Pydantic ``extra="forbid"`` and ``max_length``
already bound the request shape; this module adds the second layer of
defence on the textual content itself.
"""

from __future__ import annotations

import re
from typing import Final

INJECTION_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"ignore\s+(all\s+)?previous\s+(instructions|messages|prompts)",
        re.IGNORECASE,
    ),
    re.compile(
        r"disregard\s+(all\s+)?previous\s+(instructions|messages|prompts)",
        re.IGNORECASE,
    ),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
    re.compile(r"<\s*script[\s\S]*?>", re.IGNORECASE),
    re.compile(r"</\s*script\s*>", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"data:\s*text/html", re.IGNORECASE),
)

MAX_LENGTH: Final[int] = 2000


def sanitise_chat_message(message: str) -> str:
    """Return a sanitised copy of ``message`` suitable for the LLM.

    Args:
        message: Raw user input.

    Returns:
        The trimmed, length-bounded message with prompt-injection markers
        and trivial XSS payloads neutralised.

    """
    if not isinstance(message, str):
        raise TypeError("message must be a string")

    cleaned = message.strip()
    if not cleaned:
        return ""

    if len(cleaned) > MAX_LENGTH:
        cleaned = cleaned[:MAX_LENGTH]

    for pattern in INJECTION_PATTERNS:
        cleaned = pattern.sub("[redacted]", cleaned)

    cleaned = re.sub(r"\s{3,}", " ", cleaned)
    return cleaned
