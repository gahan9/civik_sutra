from __future__ import annotations


import asyncio
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any

import structlog

from src.models.candidate import AffidavitData, RawCandidateData

logger = structlog.get_logger(__name__)

MYNETA_BASE_URL = "https://myneta.info"
FETCH_TIMEOUT_SECONDS = 10


class _TableParser(HTMLParser):
    """Minimal HTML table parser for MyNeta candidate tables."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        super().__init__()
        self.rows: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell: list[str] = []
        self._in_td = False
        self._in_table = False
        self._table_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Execute handle_starttag operation."""
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._in_table = True
        elif tag in ("td", "th") and self._in_table:
            self._in_td = True
            self._current_cell = []

    def handle_endtag(self, tag: str) -> None:
        """Execute handle_endtag operation."""
        if tag in ("td", "th") and self._in_td:
            self._in_td = False
            self._current_row.append(" ".join(self._current_cell).strip())
        elif tag == "tr" and self._in_table:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = []
        elif tag == "table":
            self._table_depth -= 1
            if self._table_depth == 0:
                self._in_table = False

    def handle_data(self, data: str) -> None:
        """Execute handle_data operation."""
        if self._in_td:
            self._current_cell.append(data.strip())


class ScraperService:
    """Extracts structured candidate data from public sources."""

    async def fetch_myneta_candidates(
        self,
        constituency: str,
    ) -> list[RawCandidateData]:
        """Fetch candidate list from MyNeta.info for a constituency.

        MyNeta URL pattern: https://myneta.info/{election}/{constituency}
        Parse HTML table for: name, party, education, criminal cases,
        total assets, total liabilities.

        Defensive: if HTML structure changes, return empty list and log
        warning so the caller can fall back to Gemini grounding search.
        """
        slug = self._constituency_slug(constituency)
        html = await self._fetch_page(f"{MYNETA_BASE_URL}/ls2024/{slug}")
        if not html:
            logger.warning(
                "myneta_fetch_failed",
                constituency=constituency,
                slug=slug,
            )
            return []

        return self._parse_candidate_table(html, constituency)

    async def fetch_eci_affidavit(
        self,
        candidate_id: str,
    ) -> AffidavitData | None:
        """Fetch candidate's election affidavit from ECI.

        Returns None when unavailable. Future: Vision API OCR for scanned PDFs.
        """
        logger.info("eci_affidavit_stub", candidate_id=candidate_id)
        return None

    def _parse_candidate_table(
        self,
        html: str,
        constituency: str,
    ) -> list[RawCandidateData]:
        parser = _TableParser()
        try:
            parser.feed(html)
        except Exception:
            logger.warning("html_parse_error", constituency=constituency)
            return []

        candidates: list[RawCandidateData] = []
        for row in parser.rows[1:]:
            parsed = self._row_to_candidate(row)
            if parsed:
                candidates.append(parsed)

        logger.info(
            "myneta_parsed",
            constituency=constituency,
            candidate_count=len(candidates),
        )
        return candidates

    @staticmethod
    def _row_to_candidate(row: list[str]) -> RawCandidateData | None:
        if len(row) < 4:
            return None
        try:
            name = row[1] if len(row) > 1 else row[0]
            party = row[2] if len(row) > 2 else "Independent"
            criminal = ScraperService._parse_int(row[3]) if len(row) > 3 else 0
            education = row[4] if len(row) > 4 else "Not declared"
            assets = ScraperService._parse_currency(row[5]) if len(row) > 5 else 0
            liabilities = ScraperService._parse_currency(row[6]) if len(row) > 6 else 0

            return RawCandidateData(
                name=name,
                party=party,
                education=education,
                criminal_cases=criminal,
                total_assets_inr=assets,
                total_liabilities_inr=liabilities,
            )
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _parse_int(value: str) -> int:
        digits = re.sub(r"[^\d]", "", value)
        return int(digits) if digits else 0

    @staticmethod
    def _parse_currency(value: str) -> int:
        cleaned = re.sub(r"[^\d.]", "", value.replace(",", ""))
        if not cleaned:
            return 0
        try:
            amount = float(cleaned)
            if "crore" in value.lower() or "cr" in value.lower():
                amount *= 10_000_000
            elif "lakh" in value.lower() or "lac" in value.lower():
                amount *= 100_000
            return int(amount)
        except ValueError:
            return 0

    @staticmethod
    def _constituency_slug(name: str) -> str:
        slug = name.strip().lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        return urllib.parse.quote(slug, safe="-")

    async def _fetch_page(self, url: str) -> str | None:
        def _do_fetch() -> str | None:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "CivikSutra/1.0 (election-education)"},
                )
                with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
                    return str(resp.read().decode("utf-8", errors="replace"))
            except (OSError, TimeoutError):
                return None

        return await asyncio.to_thread(_do_fetch)

    async def _fetch_json(self, url: str) -> dict[str, Any] | None:
        def _do_fetch() -> dict[str, Any] | None:
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
                    body = resp.read().decode("utf-8")
                data = json.loads(body)
                return data if isinstance(data, dict) else None
            except (OSError, TimeoutError, json.JSONDecodeError):
                return None

        return await asyncio.to_thread(_do_fetch)
